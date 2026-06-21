import { NavigationContainer } from '@react-navigation/native'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { createStackNavigator } from '@react-navigation/stack'
import { View, Text, StyleSheet } from 'react-native'
import type { WorkspaceType } from '../types'
import { WORKSPACE_COLORS, WORKSPACE_LABELS } from '../types'

import HomeScreen from '../screens/HomeScreen'
import WorkspaceScreen from '../screens/WorkspaceScreen'
import CouncilScreen from '../screens/CouncilScreen'
import MissionControlScreen from '../screens/MissionControlScreen'
import SettingsScreen from '../screens/SettingsScreen'

const Tab = createBottomTabNavigator()
const Stack = createStackNavigator()

function TabIcon({ label, focused, color }: { label: string; focused: boolean; color: string }) {
  const icons: Record<string, string> = {
    Home: '⌂',
    Workspace: '⊞',
    Council: '◎',
    Settings: '⚙',
  }
  return (
    <View style={[styles.tabIcon, focused && { borderColor: color, borderWidth: 1 }]}>
      <Text style={[styles.tabIconText, { color: focused ? color : '#666' }]}>
        {icons[label] || '○'}
      </Text>
    </View>
  )
}

function HomeTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarActiveTintColor: '#fff',
        tabBarInactiveTintColor: '#666',
        tabBarIcon: ({ focused, color }) => (
          <TabIcon label={route.name} focused={focused} color={color as string} />
        ),
        tabBarLabelStyle: styles.tabLabel,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Workspace" component={WorkspaceScreen} />
      <Tab.Screen name="Council" component={CouncilScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  )
}

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Main" component={HomeTabs} />
        <Stack.Screen name="MissionControl" component={MissionControlScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  )
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: '#0A0A0A',
    borderTopColor: 'rgba(255,255,255,0.08)',
    borderTopWidth: 1,
    paddingTop: 4,
    height: 60,
  },
  tabLabel: {
    fontSize: 10,
    fontWeight: '500',
  },
  tabIcon: {
    width: 28,
    height: 28,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabIconText: {
    fontSize: 16,
  },
})
