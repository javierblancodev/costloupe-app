import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { Plus, Trash2 } from "lucide-react"
import { Suspense } from "react"

import { ProjectsService } from "@/client"
import type { Recommendation } from "@/components/Projects/ProjectResult"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

function getProjectsQueryOptions() {
  return {
    queryFn: async () =>
      (await ProjectsService.readProjects({ query: { skip: 0, limit: 100 } }))
        .data,
    queryKey: ["projects"],
  }
}

export const Route = createFileRoute("/_layout/projects")({
  component: Projects,
  head: () => ({
    meta: [{ title: "Designs - Costloupe" }],
  }),
})

function ProjectsListContent() {
  const { data } = useSuspenseQuery(getProjectsQueryOptions())
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const deleteMutation = useMutation({
    mutationFn: (id: string) => ProjectsService.deleteProject({ path: { id } }),
    onSuccess: () => showSuccessToast("Design deleted"),
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] })
    },
  })

  if (data.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <h3 className="text-lg font-semibold">
          You don't have any designs yet
        </h3>
        <p className="text-muted-foreground">
          Start a new design to get a recommendation
        </p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {data.data.map((project) => {
        const recommendation = project.recommendation as Recommendation | null
        return (
          <Card key={project.id}>
            <CardHeader>
              <CardTitle>{project.name}</CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-between">
              {recommendation ? (
                <div className="flex flex-col">
                  <span>{recommendation.name}</span>
                  <span className="font-semibold">
                    ${recommendation.monthly_cost.toFixed(2)}/mo
                  </span>
                </div>
              ) : (
                <span className="text-muted-foreground">No recommendation</span>
              )}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => deleteMutation.mutate(project.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

function Projects() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Designs</h1>
          <p className="text-muted-foreground">
            Get a cost-oriented infrastructure recommendation
          </p>
        </div>
        <Button asChild>
          <Link to="/new-design">
            <Plus className="mr-2" />
            New design
          </Link>
        </Button>
      </div>
      <Suspense fallback={<p className="text-muted-foreground">Loading...</p>}>
        <ProjectsListContent />
      </Suspense>
    </div>
  )
}
