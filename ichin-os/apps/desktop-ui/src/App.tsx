import AppShell from './components/Shell/AppShell'
import OnboardingFlow from './components/Zoey/OnboardingFlow'
import { useUIStore } from './stores/uiStore'

export default function App() {
  const onboardingComplete = useUIStore((s) => s.onboardingComplete)

  if (!onboardingComplete) {
    return <OnboardingFlow />
  }

  return <AppShell />
}
