import { View, StyleSheet } from 'react-native'
import type { WorkspaceType } from '../types'
import { WORKSPACE_COLORS } from '../types'
import { useWorkspaceStore } from '../stores/workspaceStore'
import StudyWorkspace from './Workspaces/StudyWorkspace'
import CodingWorkspace from './Workspaces/CodingWorkspace'
import LearningWorkspace from './Workspaces/LearningWorkspace'
import PersonalWorkspace from './Workspaces/PersonalWorkspace'

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
    <View style={[styles.container, { borderLeftColor: color, borderLeftWidth: 2 }]}>
      <Component />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0A0A',
  },
})
