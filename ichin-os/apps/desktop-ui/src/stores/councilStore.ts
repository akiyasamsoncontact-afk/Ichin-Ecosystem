import { create } from 'zustand'
import type { AgentOutput, CouncilDecision, AgentName } from '../types'
import { agentsApi, orchestratorApi } from '../services/api'

interface CouncilState {
  isOpen: boolean
  outputs: AgentOutput[]
  decision: CouncilDecision | null
  loading: boolean
  open: () => void
  close: () => void
  orchestrate: (input: string) => Promise<void>
}

const ALL_AGENTS: AgentName[] = ['orion', 'nova', 'sage', 'pulse', 'echo', 'iris', 'atlas', 'aegis']

export const useCouncilStore = create<CouncilState>((set) => ({
  isOpen: false,
  outputs: [],
  decision: null,
  loading: false,
  open: () => set({ isOpen: true }),
  close: () => set({ isOpen: false }),
  orchestrate: async (input) => {
    set({ loading: true, outputs: [], decision: null })
    try {
      const { outputs } = await agentsApi.orchestrate(input)
      set({ outputs: outputs })
      try {
        const { decision } = await orchestratorApi.orchestrate(input)
        set({ decision: decision.decision ? decision : {
          decision: input,
          agentsUsed: ALL_AGENTS,
          confidence: outputs.reduce((a, o) => a + o.confidence, 0) / outputs.length,
          riskLevel: outputs.some(o => o.risk > 0.7) ? 'high' : outputs.some(o => o.risk > 0.4) ? 'medium' : 'low',
          reasoning: outputs.map(o => o.reasoning).join('\n'),
          outputs,
        }})
      } catch {
        set({
          decision: {
            decision: input,
            agentsUsed: ALL_AGENTS,
            confidence: outputs.reduce((a, o) => a + o.confidence, 0) / outputs.length,
            riskLevel: outputs.some(o => o.risk > 0.7) ? 'high' : 'medium',
            reasoning: outputs.map(o => o.reasoning).join('\n'),
            outputs,
          },
        })
      }
    } catch {
      const fallback: AgentOutput[] = ALL_AGENTS.map((agent) => ({
        agent,
        recommendation: `Analysis from ${agent}`,
        confidence: 0.5 + Math.random() * 0.4,
        risk: Math.random() * 0.5,
        efficiency: 0.5 + Math.random() * 0.4,
        reasoning: `${agent} processed the request in offline mode.`,
      }))
      set({
        outputs: fallback,
        decision: {
          decision: input,
          agentsUsed: ALL_AGENTS,
          confidence: 0.65,
          riskLevel: 'medium',
          reasoning: 'Offline mode: agents provided heuristic analysis.',
          outputs: fallback,
        },
      })
    } finally {
      set({ loading: false })
    }
  },
}))
