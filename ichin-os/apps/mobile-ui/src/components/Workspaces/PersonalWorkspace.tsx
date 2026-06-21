import { useState } from 'react'
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet } from 'react-native'

const EVENTS = [
  { time: '09:00', title: 'Team standup' },
  { time: '11:30', title: 'Design review' },
  { time: '14:00', title: 'Deep work block' },
  { time: '16:00', title: 'Project sync' },
]

interface Task {
  id: string
  title: string
  completed: boolean
}

const SAMPLE_TASKS: Task[] = [
  { id: '1', title: 'Review quarterly goals', completed: false },
  { id: '2', title: 'Prepare presentation slides', completed: true },
  { id: '3', title: 'Read AI paper', completed: false },
  { id: '4', title: 'Update portfolio', completed: false },
]

export default function PersonalWorkspace() {
  const [tasks, setTasks] = useState<Task[]>(SAMPLE_TASKS)
  const [newTask, setNewTask] = useState('')

  const toggleTask = (id: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    )
  }

  const addTask = () => {
    if (!newTask.trim()) return
    setTasks([...tasks, { id: Date.now().toString(), title: newTask, completed: false }])
    setNewTask('')
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.timelineCard}>
        <Text style={styles.sectionTitle}>Today's Timeline</Text>
        {EVENTS.map((e) => (
          <View key={e.time} style={styles.eventRow}>
            <Text style={styles.eventTime}>{e.time}</Text>
            <View style={styles.eventLine} />
            <Text style={styles.eventTitle}>{e.title}</Text>
          </View>
        ))}
      </View>

      <View style={styles.taskCard}>
        <View style={styles.taskHeader}>
          <Text style={styles.sectionTitle}>Tasks</Text>
          <Text style={styles.taskCount}>
            {tasks.filter((t) => t.completed).length}/{tasks.length}
          </Text>
        </View>
        {tasks.map((task) => (
          <View key={task.id} style={styles.taskRow}>
            <TouchableOpacity onPress={() => toggleTask(task.id)}>
              <Text style={[styles.checkbox, task.completed && { color: '#9E9E9E' }]}>
                {task.completed ? '✓' : '○'}
              </Text>
            </TouchableOpacity>
            <Text
              style={[
                styles.taskTitle,
                task.completed && { color: 'rgba(255,255,255,0.3)', textDecorationLine: 'line-through' },
              ]}
            >
              {task.title}
            </Text>
          </View>
        ))}
        <View style={styles.addRow}>
          <TextInput
            value={newTask}
            onChangeText={setNewTask}
            onSubmitEditing={addTask}
            placeholder="Add a task..."
            placeholderTextColor="rgba(255,255,255,0.2)"
            style={styles.taskInput}
          />
          <TouchableOpacity onPress={addTask}>
            <Text style={styles.addBtn}>+</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.aiCard}>
        <Text style={styles.aiTitle}>✦ AI Productivity</Text>
        <Text style={styles.aiSuggestion}>• Block 2 hours for deep work on project</Text>
        <Text style={styles.aiSuggestion}>• Review pending emails before noon</Text>
        <Text style={styles.aiSuggestion}>• Take a 15-min break every 90 mins</Text>
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'rgba(158, 158, 158, 0.02)',
  },
  content: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.3)',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 10,
  },
  timelineCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  eventRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  eventTime: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.3)',
    width: 44,
    textAlign: 'right',
    marginRight: 10,
  },
  eventLine: {
    width: 1,
    height: 24,
    backgroundColor: 'rgba(255,255,255,0.05)',
    marginRight: 10,
  },
  eventTitle: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.7)',
  },
  taskCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  taskCount: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.2)',
  },
  taskRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  checkbox: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.2)',
    marginRight: 10,
    width: 20,
  },
  taskTitle: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.7)',
    flex: 1,
  },
  addRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
  },
  taskInput: {
    flex: 1,
    fontSize: 13,
    color: 'rgba(255,255,255,0.6)',
  },
  addBtn: {
    fontSize: 18,
    color: 'rgba(255,255,255,0.3)',
    padding: 4,
  },
  aiCard: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 16,
    padding: 16,
  },
  aiTitle: {
    fontSize: 13,
    color: 'rgba(255,255,255,0.5)',
    marginBottom: 10,
  },
  aiSuggestion: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.3)',
    marginBottom: 6,
    paddingLeft: 8,
  },
})
