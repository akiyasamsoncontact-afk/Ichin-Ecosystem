import { useWorkspaceStore } from '../stores/workspaceStore'
import { WORKSPACE_COLORS } from '../types'
import type { WorkspaceType } from '../types'
import StudyWorkspace from './Workspace/StudyWorkspace'
import CodingWorkspace from './Workspace/CodingWorkspace'
import LearningWorkspace from './Workspace/LearningWorkspace'
import PersonalWorkspace from './Workspace/PersonalWorkspace'

const COMPONENTS: Record<WorkspaceType, React.ComponentType> = {
  study: StudyWorkspace,
  coding: CodingWorkspace,
  learning: LearningWorkspace,
  personal: PersonalWorkspace,
}

export default function WorkspaceContainer() {
  const active = useWorkspaceStore((s) => s.active)
  const Component = COMPONENTS[active]
  const color = WORKSPACE_COLORS[active]

  return (
    <div style={{
      height: '100%',
      borderLeft: `2px solid ${color}`,
      backgroundColor: color + '04',
    }}>
      <Component />
    </div>
  )
}
