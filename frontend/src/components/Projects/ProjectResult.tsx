import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export type Recommendation = {
  archetype: string
  name: string
  services: string[]
  monthly_cost: number
  config: Record<string, string>
  candidates: { archetype: string; monthly_cost: number }[]
}

function ProjectResult({ recommendation }: { recommendation: Recommendation }) {
  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>{recommendation.name}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div>
            <p className="text-sm text-muted-foreground">
              Estimated monthly cost
            </p>
            <p className="text-3xl font-bold">
              ${recommendation.monthly_cost.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-2">Services</p>
            <div className="flex flex-wrap gap-2">
              {recommendation.services.map((service) => (
                <span
                  key={service}
                  className="rounded-md bg-muted px-2 py-1 text-sm"
                >
                  {service}
                </span>
              ))}
            </div>
          </div>
          {Object.keys(recommendation.config).length > 0 && (
            <div>
              <p className="text-sm text-muted-foreground mb-2">
                Configuration
              </p>
              <ul className="text-sm flex flex-col gap-1">
                {Object.entries(recommendation.config).map(([key, value]) => (
                  <li key={key} className="flex justify-between">
                    <span className="text-muted-foreground">
                      {key.replace(/_/g, " ")}
                    </span>
                    <span>{value}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
      {recommendation.candidates.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Other options considered</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col gap-1 text-sm">
              {recommendation.candidates.map((candidate) => (
                <li key={candidate.archetype} className="flex justify-between">
                  <span>{candidate.archetype.replace(/_/g, " ")}</span>
                  <span>${candidate.monthly_cost.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ProjectResult
