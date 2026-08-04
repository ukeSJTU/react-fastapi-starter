import { defineConfig } from "orval"

export default defineConfig({
  api: {
    input: {
      target: "../openapi.json",
    },
    output: {
      target: "./src/api/generated/endpoints/api.ts",
      schemas: {
        path: "./src/api/generated/models",
        type: "zod",
      },
      client: "react-query",
      httpClient: "fetch",
      mode: "tags-split",
      clean: true,
      indexFiles: true,
      tagsSplitDeduplication: false,
      urlEncodeParameters: true,
      mock: {
        indexMockFiles: true,
        generators: [
          {
            type: "msw",
            useExamples: true,
          },
          {
            type: "faker",
            useExamples: true,
            schemas: true,
          },
        ],
      },
      override: {
        useNamedParameters: true,
        fetch: {
          forceSuccessResponse: true,
          includeHttpResponseReturnType: true,
        },
        query: {
          signal: true,
          useOperationIdAsQueryKey: true,
        },
        zod: {
          version: 4,
          variant: "classic",
          exactOptional: true,
          generateReusableSchemas: true,
        },
      },
    },
  },
})
