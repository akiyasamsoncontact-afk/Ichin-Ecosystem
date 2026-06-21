import axios from 'axios'
import type { AppListItem, AppDetail, AppReview, AppRating, AppSubmission, InstalledApp, Category } from './types'

const client = axios.create({ baseURL: '/api/store' })

export async function fetchApps(category?: string, search?: string): Promise<AppListItem[]> {
  const params: Record<string, string> = {}
  if (category) params.category = category
  if (search) params.search = search
  const res = await client.get('/apps', { params })
  return res.data
}

export async function fetchApp(id: string): Promise<AppDetail> {
  const res = await client.get(`/apps/${id}`)
  return res.data
}

export async function installApp(id: string): Promise<{ id: string; appId: string; status: string }> {
  const res = await client.post(`/apps/${id}/install`)
  return res.data
}

export async function uninstallApp(id: string): Promise<{ status: string; appId: string }> {
  const res = await client.post(`/apps/${id}/uninstall`)
  return res.data
}

export async function fetchInstalled(): Promise<InstalledApp[]> {
  const res = await client.get('/installed')
  return res.data
}

export async function fetchCategories(): Promise<Category[]> {
  const res = await client.get('/categories')
  return res.data
}

export async function submitApp(submission: AppSubmission): Promise<{ id: string; status: string }> {
  const res = await client.post('/apps', submission)
  return res.data
}

export async function reviewApp(id: string): Promise<AppReview> {
  const res = await client.post(`/apps/${id}/review`)
  return res.data
}

export async function fetchReviews(id: string): Promise<AppReview[]> {
  const res = await client.get(`/apps/${id}/reviews`)
  return res.data
}

export async function rateApp(id: string, rating: { userId: string; score: number; comment?: string }): Promise<AppRating> {
  const res = await client.post(`/apps/${id}/rate`, rating)
  return res.data
}
