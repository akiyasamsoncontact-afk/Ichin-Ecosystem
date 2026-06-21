import { useState } from 'react'
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet } from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const AGENT_INFO: { name: string; role: string; color: string }[] = [
  { name: 'orion', role: 'Strategic Planner', color: '#4A9EFF' },
  { name: 'nova', role: 'Creative Innovator', color: '#FF6B6B' },
  { name: 'sage', role: 'Knowledge Expert', color: '#B388FF' },
  { name: 'pulse', role: 'System Monitor', color: '#00E676' },
  { name: 'echo', role: 'Communication', color: '#FFB300' },
  { name: 'iris', role: 'Visual Analyst', color: '#FF80AB' },
  { name: 'atlas', role: 'Data Navigator', color: '#40C4FF' },
  { name: 'aegis', role: 'Security Guard', color: '#FF5252' },
]

export default function CouncilScreen() {
  const insets = useSafeAreaInsets()
  const [input, setInput] = useState('')
  const [outputs, setOutputs] = useState<typeof AGENT_INFO.map(() => ({ recommendation: string; confidence: number; risk: number }))>([])
  const [loading, setLoading] = useState(false)

  const handleOrchestrate = async () => {
    if (!input.trim()) return
    setLoading(true)
    await new Promise((r) => setTimeout(r, 800))
    setOutputs(
      AGENT_INFO.map(() => ({
        recommendation: `Analysis for: "${input}"`,
        confidence: 0.5 + Math.random() * 0.4,
        risk: Math.random() * 0.5,
      }))
    )
    setLoading(false)
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <Text style={styles.title}>AI Council</Text>
        <Text style={styles.subtitle}>Consult all 8 agents</Text>
      </View>

      <View style={styles.inputRow}>
        <TextInput
          value={input}
          onChangeText={setInput}
          placeholder="What would you like the council to decide?"
          placeholderTextColor="rgba(255,255,255,0.2)"
          style={styles.input}
          returnKeyType="send"
          onSubmitEditing={handleOrchestrate}
        />
        <TouchableOpacity
          onPress={handleOrchestrate}
          disabled={loading || !input.trim()}
          style={[styles.orchestrateBtn, (loading || !input.trim()) && { opacity: 0.3 }]}
        >
          <Text style={styles.orchestrateBtnText}>Consult</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.results}>
        {loading && (
          <View style={styles.loading}>
            <Text style={styles.loadingText}>Consulting all agents...</Text>
          </View>
        )}
        {outputs.length > 0 && (
          <View style={styles.grid}>
            {AGENT_INFO.map((agent, i) => (
              <View key={agent.name} style={[styles.agentCard, { borderLeftColor: agent.color }]}>
                <View style={styles.agentHeader}>
                  <Text style={styles.agentName}>{agent.name}</Text>
                  <Text style={styles.agentRole}>{agent.role}</Text>
                </View>
                <Text style={styles.agentRec} numberOfLines={2}>{outputs[i]?.recommendation}</Text>
                <View style={styles.metrics}>
                  <Text style={[styles.metric, { color: (outputs[i]?.confidence || 0) > 0.7 ? '#00E676' : '#FFB300' }]}>
                    {((outputs[i]?.confidence || 0) * 100).toFixed(0)}%
                  </Text>
                  <Text style={[styles.metric, { color: (outputs[i]?.risk || 0) > 0.5 ? '#FF5252' : '#B0B0B0' }]}>
                    Risk: {((outputs[i]?.risk || 0) * 100).toFixed(0)}%
                  </Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0A0A',
    paddingHorizontal: 16,
  },
  header: {
    paddingVertical: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.8)',
  },
  subtitle: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.4)',
    marginTop: 4,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    paddingLeft: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    marginBottom: 16,
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 13,
    paddingVertical: 12,
  },
  orchestrateBtn: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 10,
    margin: 4,
  },
  orchestrateBtnText: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 12,
    fontWeight: '500',
  },
  results: {
    flex: 1,
  },
  loading: {
    padding: 24,
    alignItems: 'center',
  },
  loadingText: {
    color: 'rgba(255,255,255,0.3)',
    fontSize: 13,
  },
  grid: {
    gap: 8,
    paddingBottom: 20,
  },
  agentCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 12,
    borderLeftWidth: 2,
  },
  agentHeader: {
    flexDirection: 'row',
    gap: 6,
    marginBottom: 4,
  },
  agentName: {
    fontSize: 12,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.8)',
    textTransform: 'capitalize',
  },
  agentRole: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.3)',
  },
  agentRec: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.5)',
    marginBottom: 6,
  },
  metrics: {
    flexDirection: 'row',
    gap: 12,
  },
  metric: {
    fontSize: 10,
    fontWeight: '500',
  },
})
