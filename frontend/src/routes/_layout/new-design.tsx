import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { useState } from "react"

import { type ProjectCreate, ProjectsService } from "@/client"
import ProjectResult, {
  type Recommendation,
} from "@/components/Projects/ProjectResult"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/new-design")({
  component: NewDesign,
  head: () => ({
    meta: [{ title: "New design - Costloupe" }],
  }),
})

type Question = {
  id: string
  prompt: string
  options?: { value: string; label: string }[]
  type?: string
  unit?: string
}

function NewDesign() {
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()
  const [name, setName] = useState("")
  const [step, setStep] = useState(-1)
  const [answers, setAnswers] = useState<Record<string, unknown>>({})
  const [result, setResult] = useState<Recommendation | null>(null)

  const { data: questions } = useQuery({
    queryKey: ["questionnaire"],
    queryFn: async () =>
      (await ProjectsService.readQuestionnaire()).data as Question[],
  })

  const mutation = useMutation({
    mutationFn: (data: ProjectCreate) =>
      ProjectsService.createProject({ body: data }),
    onSuccess: (response) => {
      setResult(response.data.recommendation as Recommendation)
      queryClient.invalidateQueries({ queryKey: ["projects"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  if (result) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col gap-6">
        <ProjectResult recommendation={result} />
        <Button asChild variant="outline">
          <Link to="/projects">Back to designs</Link>
        </Button>
      </div>
    )
  }

  if (!questions) {
    return null
  }

  if (step === -1) {
    return (
      <Card className="mx-auto max-w-xl">
        <CardHeader>
          <CardTitle>New design</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-muted-foreground">
            Give the design a name to begin.
          </p>
          <Input
            placeholder="Name"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <Button disabled={!name} onClick={() => setStep(0)}>
            Start
          </Button>
        </CardContent>
      </Card>
    )
  }

  const question = questions[step]
  const answer = answers[question.id]
  const isLast = step === questions.length - 1

  const setAnswer = (value: unknown) =>
    setAnswers((prev) => ({ ...prev, [question.id]: value }))

  const next = () => {
    if (isLast) {
      mutation.mutate({ name, answers })
    } else {
      setStep(step + 1)
    }
  }

  return (
    <Card className="mx-auto max-w-xl">
      <CardHeader>
        <CardTitle>
          Question {step + 1} of {questions.length}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <p className="text-lg">{question.prompt}</p>
        {question.type === "number" ? (
          <Input
            type="number"
            placeholder={question.unit}
            value={answer === undefined ? "" : String(answer)}
            onChange={(event) => setAnswer(Number(event.target.value))}
          />
        ) : (
          <div className="flex flex-col gap-2">
            {question.options?.map((option) => (
              <Button
                key={option.value}
                variant={answer === option.value ? "default" : "outline"}
                className="justify-start"
                onClick={() => setAnswer(option.value)}
              >
                {option.label}
              </Button>
            ))}
          </div>
        )}
        <div className="flex justify-between">
          <Button
            variant="ghost"
            disabled={step === 0}
            onClick={() => setStep(step - 1)}
          >
            Back
          </Button>
          <LoadingButton
            loading={mutation.isPending}
            disabled={answer === undefined || answer === ""}
            onClick={next}
          >
            {isLast ? "See recommendation" : "Next"}
          </LoadingButton>
        </div>
      </CardContent>
    </Card>
  )
}
