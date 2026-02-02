use std::io::{self, Write};
use rusqlite::{params, Connection, Result};
// Add this struct definition or import the Console type from the appropriate crate/module
pub struct Console;

// You can implement default values in Rust using the Default trait.
pub struct TodoApp {
    todo_ids: Vec<i32>,
    todos: Vec<String>,
    status: Vec<i32>, // Private field
    file_path_to_db: std::path::PathBuf,
    console: Console, // Private field
}

// Implement Default for TodoApp
impl Default for TodoApp {
    fn default() -> Self {
        TodoApp {
            todo_ids: Vec::new(),
            todos: Vec::new(),
            status: Vec::new(),
            file_path_to_db: std::path::PathBuf::from("./.todo_list.db"),
            console: Console,
        }
    }

    fn new(filepath: & str, text: & str) -> Self {
        let mut app = TodoApp::default();
        app.file_path_to_db = std::path::PathBuf::from(filepath);
        app.add_todo(text);
        app
    }
// Example of a static/class-level attribute in Rust:
impl TodoApp {
    // Associated constant (like a static class attribute)
    pub const APP_NAME: &'static str = "Todo CLI App";
    pub const APP_VERSION: &'static str = "1.0.0";
}

impl TodoApp {
    pub fn add_todo(& mut self, item: & str) {
        let item = item.trim();
        if item.is_empty() {
            println!("Error: Todo item cannot be empty.");
            return;
        }
        let new_id = if let Some(&last_id) = self.todo_ids.last() {
            last_id + 1
        } else {
            1
        };
        self.todo_ids.push(new_id);
        self.todos.push(item.to_string());
        self.status.push(0); // 0 for pending
        println!("Added todo item: {}", item);
        }

    pub fn list_todos(& self) {
        if self.todos.is_empty() {
            println!("No todo items found.");
            return;
        }
        println!("Todo List:");
        for (index, todo) in self.todos.iter().enumerate() {
            let status = if self.status[index] == 1 { "Done" } else { "Pending" };
            println!("{}: {} [{}]", self.todo_ids[index], todo, status);
        }
        }

    pub fn clear_all(& mut self) {
        println!("Are you sure you want to clear all todo items? (y/n): ");
        io::stdout().flush().unwrap();

        let mut input = String::new();
        if io::stdin().read_line(&mut input).is_ok() {
            let input = input.trim().to_lowercase();
            if input == "y" || input == "yes" {
                self.todo_ids.clear();
                self.todos.clear();
                self.status.clear();
                println!("All todo items have been cleared.");
            } else {
                println!("Clear operation cancelled.");
            }
        } else {
            println!("Failed to read input. Clear operation cancelled.");
        }
    }

    pub fn remove_todo(& mut self, id: i32) {
        if let Some(pos) = self.todo_ids.iter().position(|&x| x == id) {
            self.todo_ids.remove(pos);
            self.todos.remove(pos);
            self.status.remove(pos);
            println!("Removed todo item with ID: {}", id);
        } else {
            println!("Todo item with ID: {} not found.", id);
        }
    }

    fn check_and_load_todos(& mut self) {
        let conn = match Connection::open(&self.file_path_to_db) {
            Ok(c) => c,
            Err(e) => {
                println!("Failed to open database: {}", e);
                return;
            }
        };

        let mut stmt = match conn.prepare("SELECT id, item, done FROM todos") {
            Ok(s) => s,
            Err(e) => {
                println!("Failed to prepare statement: {}", e);
                return;
            }
        };

        let todo_iter = match stmt.query_map([], |row| {
            Ok((
                row.get::<_, i32>(0)?,
                row.get::<_, String>(1)?,
                row.get::<_, i32>(2)?,
            ))
        }) {
            Ok(iter) => iter,
            Err(e) => {
                println!("Failed to query todos: {}", e);
                return;
            }
        };

        self.todo_ids.clear();
        self.todos.clear();
        self.status.clear();

        for todo in todo_iter {
            match todo {
                Ok((id, todo, status)) => {
                    self.todo_ids.push(id);
                    self.todos.push(todo);
                    self.status.push(status);
                }
                Err(e) => {
                    println!("Error loading todo: {}", e);
                }
            }
        }
    }


}



fn main() {
    let mut _app = TodoApp::default();
    _app.check_and_load_todos();
    _app.list_todos();
}