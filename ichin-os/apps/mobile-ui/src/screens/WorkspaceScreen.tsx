import { View, StyleSheet } from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import Shell from '../components/Shell'
import WorkspaceContainer from '../components/WorkspaceContainer'
import FocusOverlay from '../components/FocusOverlay'
import AIOrb from '../components/AIOrb'

export default function WorkspaceScreen() {
  const insets = useSafeAreaInsets()

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <Shell />
      <FocusOverlay />
      <WorkspaceContainer />
      <AIOrb />
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0A0A',
  },
})
