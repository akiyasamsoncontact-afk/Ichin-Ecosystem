# CalenTask - Modern Calendar & To-Do Application

A minimal, productivity-focused calendar and task management application inspired by Notion, Linear, and Apple Calendar.

## Features

- **Calendar Views**: Month, Week, and Day views with smooth transitions
- **Task Management**: Create, edit, delete tasks with priorities and statuses
- **Glass UI Design**: Liquid glass aesthetic with frosted panels
- **Dark/Light Mode**: Full theme support
- **Keyboard Shortcuts**: Cmd/Ctrl+K for command palette
- **Offline Support**: All data stored in localStorage

## File Structure

- `index.html` - Main entry point
- `app.js` - Main application component
- `styles/theme.css` - Theme variables and glass styles
- `utils/storage.js` - LocalStorage utilities
- `utils/dateUtils.js` - Date helper functions
- `components/` - React components

## Components

- `Sidebar` - Navigation sidebar
- `CalendarHeader` - Calendar controls and view toggles
- `MonthView`, `WeekView`, `DayView` - Calendar views
- `TaskItem` - Individual task display
- `TaskPanel` - Task details sidebar
- `TaskModal` - New task creation modal
- `CommandPalette` - Quick search and commands

## Maintenance Notes

**Important**: When updating this project, always check if README.md needs updates for:
- New features added
- File structure changes
- Component additions/removals
- API changes