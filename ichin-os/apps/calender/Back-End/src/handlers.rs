use std::sync::Arc;

use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use tracing::error;

use crate::db::Database;
use crate::models::{ApiResponse, CreateTaskRequest, Task, UpdateTaskRequest};

pub async fn get_tasks(
    State(db): State<Arc<Database>>,
) -> Json<ApiResponse<Vec<Task>>> {
    match db.get_all_tasks() {
        Ok(tasks) => Json(ApiResponse {
            success: true,
            data: Some(tasks),
            error: None,
        }),
        Err(e) => {
            error!("Failed to get tasks: {}", e);
            Json(ApiResponse {
                success: false,
                data: None,
                error: Some(e.to_string()),
            })
        }
    }
}

pub async fn create_task(
    State(db): State<Arc<Database>>,
    Json(req): Json<CreateTaskRequest>,
) -> (StatusCode, Json<ApiResponse<Task>>) {
    let task = Task {
        id: uuid::Uuid::new_v4().to_string(),
        title: req.title,
        description: req.description.unwrap_or_default(),
        due_date: req.due_date.unwrap_or_default(),
        priority: req.priority.unwrap_or_else(|| "medium".to_string()),
        status: req.status.unwrap_or_else(|| "todo".to_string()),
        tags: req.tags.unwrap_or_default(),
        created_at: chrono::Utc::now().to_rfc3339(),
    };

    match db.create_task(&task) {
        Ok(_) => (StatusCode::CREATED, Json(ApiResponse {
            success: true,
            data: Some(task),
            error: None,
        })),
        Err(e) => {
            error!("Failed to create task: {}", e);
            (StatusCode::INTERNAL_SERVER_ERROR, Json(ApiResponse {
                success: false,
                data: None,
                error: Some(e.to_string()),
            }))
        }
    }
}

pub async fn update_task(
    State(db): State<Arc<Database>>,
    Path(id): Path<String>,
    Json(req): Json<UpdateTaskRequest>,
) -> Json<ApiResponse<Task>> {
    let current = db.get_all_tasks().ok().and_then(|tasks| tasks.into_iter().find(|t| t.id == id));
    let current = match current {
        Some(t) => t,
        None => {
            return Json(ApiResponse {
                success: false,
                data: None,
                error: Some("Task not found".to_string()),
            });
        }
    };

    let task = Task {
        id: current.id.clone(),
        title: req.title.unwrap_or(current.title),
        description: req.description.unwrap_or(current.description),
        due_date: req.due_date.unwrap_or(current.due_date),
        priority: req.priority.unwrap_or(current.priority),
        status: req.status.unwrap_or(current.status),
        tags: req.tags.unwrap_or(current.tags),
        created_at: current.created_at,
    };

    match db.update_task(&id, &task) {
        Ok(true) => Json(ApiResponse {
            success: true,
            data: Some(task),
            error: None,
        }),
        Ok(false) => Json(ApiResponse {
            success: false,
            data: None,
            error: Some("Task not found".to_string()),
        }),
        Err(e) => {
            error!("Failed to update task: {}", e);
            Json(ApiResponse {
                success: false,
                data: None,
                error: Some(e.to_string()),
            })
        }
    }
}

pub async fn delete_task(
    State(db): State<Arc<Database>>,
    Path(id): Path<String>,
) -> Json<ApiResponse<()>> {
    match db.delete_task(&id) {
        Ok(true) => Json(ApiResponse {
            success: true,
            data: None,
            error: None,
        }),
        Ok(false) => Json(ApiResponse {
            success: false,
            data: None,
            error: Some("Task not found".to_string()),
        }),
        Err(e) => {
            error!("Failed to delete task: {}", e);
            Json(ApiResponse {
                success: false,
                data: None,
                error: Some(e.to_string()),
            })
        }
    }
}
