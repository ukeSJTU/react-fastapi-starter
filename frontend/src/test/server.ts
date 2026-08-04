import { setupServer } from "msw/node"

import * as generatedMocks from "@/api/generated/endpoints/index.msw"

const handlers = Object.values(generatedMocks).flatMap((getMock) => getMock())

export const server = setupServer(...handlers)
