import { useState } from 'react'
import {
  View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Modal, KeyboardAvoidingView, Platform,
} from 'react-native'
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

interface AgentOutput {
  agent: string
  recommendation: string
  confidence: number
  risk: number
}

interface Props {
  visible: boolean
  onClose: () => void
}

export default function AICouncil({ visible, onClose }: Props) {
  const insets = useSafeAreaInsets()
  const [input, setInput] = useState('')
  const [outputs, setOutputs] = useState<AgentOutput[]>([])
  const [loading, setLoading] = useState(false)

  const handleOrchestrate = async () => {
    if (!input.trim()) return
    setLoading(true)
    setOutputs([])
    const fallback: AgentOutput[] = AGENT_INFO.map((a) => ({
      agent: a.name,
      recommendation: `Analysis from ${a.name}`,
      confidence: 0.5 + Math.random() * 0.4,
      risk: Math.random() * 0.5,
    }))
    await new Promise((r) => setTimeout(r, 800))
    setOutputs(fallback)
    setLoading(false)
  }

  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <TouchableOpacity activeOpacity={1} onPress={onClose} style={styles.backdrop}>
        <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
          <TouchableOpacity activeOpacity={1} style={[styles.container, { paddingBottom: insets.bottom + 20 }]}>
            <View style={styles.handle} />
            <View style={styles.header}>
              <Text style={styles.title}>AI Council</Text>
              <TouchableOpacity onPress={onClose}>
                <Text style={styles.closeBtn}>✕</Text>
              </TouchableOpacity>
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
                <Text style={styles.orchestrateBtnText}>{loading ? '...' : '→'}</Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.results}>
              {loading && (
                <View style={styles.loading}>
                  <Text style={styles.loadingText}>Consulting agents...</Text>
                </View>
              )}
              {outputs.length > 0 && (
                <View style={styles.grid}>
                  {outputs.map((o) => {
                    const info = AGENT_INFO.find((a) => a.name === o.agent)
                    return (
                      <View key={o.agent} style={[styles.agentCard, { borderLeftColor: info?.color || '#666' }]}>
                        <View style={styles.agentHeader}>
                          <Text style={styles.agentName}>{o.agent}</Text>
                          <Text style={styles.agentRole}>{info?.role}</Text>
                        </View>
                        <Text style={styles.agentRec} numberOfLines={2}>{o.recommendation}</Text>
                        <View style={styles.metrics}>
                          <Text style={[styles.metric, { color: o.confidence > 0.7 ? '#00E676' : '#FFB300' }]}>
                            {(o.confidence * 100).toFixed(0)}%
                          </Text>
                          <Text style={[styles.metric, { color: o.risk > 0.5 ? '#FF5252' : '#B0B0B0' }]}>
                            Risk: {(o.risk * 100).toFixed(0)}%
                          </Text>
                        </View>
                      </View>
                    )
                  })}
                </View>
              )}
            </ScrollView>
          </TouchableOpacity>
        </KeyboardAvoidingView>
      </TouchableOpacity>
    </Modal>
  )
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  container: {
    backgroundColor: '#0A0A0A',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
    paddingHorizontal: 16,
  },
  handle: {
    width: 36,
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 2,
    alignSelf: 'center',
    marginTop: 8,
    marginBottom: 12,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.8)',
  },
  closeBtn: {
    fontSize: 16,
    color: 'rgba(255,255,255,0.3)',
    padding: 4,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    marginBottom: 12,
  },
  input: {
    flex: 1,
    color: '#fff',
    fontSize: 14,
    paddingVertical: 10,
  },
  orchestrateBtn: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  orchestrateBtnText: {
    color: '#fff',
    fontSize: 14,
  },
  results: {
    maxHeight: 400,
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
    gap: 6,
    paddingBottom: 16,
  },
  agentCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 10,
    padding: 10,
    borderLeftWidth: 2,
  },
  agentHeader: {
    flexDirection: 'row',
    gap: 6,
    marginBottom: 4,
  },
  agentName: {
    fontSize: 11,
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
