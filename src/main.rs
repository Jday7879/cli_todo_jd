use std::io::{self, Write};
use rusqlite::{params, Connection, Result};
use clap::{Parser, Subcommand};

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
}

// fn new(filepath: &str, text: &str) -> TodoApp {
//     let mut app = TodoApp::default();
//     app.file_path_to_db = std::path::PathBuf::from(filepath);
//     app.add_todo(text);
//     app
// }

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
        // Let the database handle unique IDs (auto-increment)
        let new_id = None::<i32>;
        let conn = self._connect_to_db().unwrap();

        let mut stmt = match conn.prepare("INSERT INTO todos (id, item, done) VALUES (?, ?, ?)") {
            Ok(s) => s,
            Err(e) => {
            println!("Failed to prepare statement: {}", e);
            return;
            }
        };

        if let Err(e) = stmt.execute(params![new_id, item, 0]) {
            println!("Failed to insert todo: {}", e);
            return;
        }
        println!("Added todo item: {}", item);
        }

    pub fn list_todos(& mut self) {
        self._check_and_load_todos();
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

    pub fn clear_all(& self) {
        println!("Are you sure you want to clear all todo items? (y/n): ");
        io::stdout().flush().unwrap();

        let mut input = String::new();
        if io::stdin().read_line(&mut input).is_ok() {
            let input = input.trim().to_lowercase();
            if input == "y" || input == "yes" {
                self._drop_all_from_db();
            } else {
                println!("Clear operation cancelled.");
            }
        } else {
            println!("Failed to read input. Clear operation cancelled.");
        }
    }

    fn _drop_all_from_db(& self) {
        let conn = self._connect_to_db().unwrap();
        if let Err(e) = conn.execute("DELETE FROM todos", []) {
            println!("Failed to clear todos from database: {}", e);
            return;
        }
        println!("All todo items have been cleared from the database.");
    }

    fn remove_todo(& self, id: i32) {
        // if let Some(pos) = self.todo_ids.iter().position(|&x| x == id) {
        //     self.todo_ids.remove(pos);
        //     self.todos.remove(pos);
        //     self.status.remove(pos);
        //     println!("Removed todo item with ID: {}", id);
        // } else {
        //     println!("Todo item with ID: {} not found.", id);
        // }

        let conn = self._connect_to_db().unwrap();
        let valid_id = match  {
            let mut stmt = conn.prepare("SELECT COUNT(*) FROM todos WHERE id = ?").unwrap();
            let count: i32 = stmt.query_row(params![id], |row| row.get(0)).unwrap();
            count > 0
        } {
            true => id,
            false => {
                println!("Todo item with ID: {} not found in database.", id);
                return;
            }
            
        };
        if let Err(e) = conn.execute("DELETE FROM todos WHERE id = ?", params![valid_id]) {
            println!("Failed to remove todo from database: {}", e);
            return;
        }
        println!("Removed todo item with ID: {}", valid_id);
    }

    fn _connect_to_db(& self) -> Option<Connection> {
        let conn = match Connection::open(&self.file_path_to_db) {
            Ok(c) => c,
            Err(e) => {
                println!("Failed to open database: {}", e);
                return None;
            }
        };
        Some(conn)
    }
    
    fn _check_and_load_todos(& mut self) {
        let conn =  self._connect_to_db().unwrap();

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

    pub fn mark_as_done(& self, id: i32) {
        let conn = self._connect_to_db().unwrap();

        let valid_id = match  {
            let mut stmt = conn.prepare("SELECT COUNT(*) FROM todos WHERE id = ?").unwrap();
            let count: i32 = stmt.query_row(params![id], |row| row.get(0)).unwrap();
            count > 0
        } {
            true => id,
            false => {
                println!("Todo item with ID: {} not found in database.", id);
                return;
            }
            
        };

        if let Err(e) = conn.execute("UPDATE todos SET done = 1 WHERE id = ?", params![valid_id]) {
            println!("Failed to mark todo as done: {}", e);
            return;
        }
        println!("Marked todo item with ID: {} as done.", valid_id);
    }

    pub fn mark_as_not_done(& self, id: i32) {
        let conn = self._connect_to_db().unwrap();

        let valid_id = match  {
            let mut stmt = conn.prepare("SELECT COUNT(*) FROM todos WHERE id = ?").unwrap();
            let count: i32 = stmt.query_row(params![id], |row| row.get(0)).unwrap();
            count > 0
        } {
            true => id,
            false => {
                println!("Todo item with ID: {} not found in database.", id);
                return;
            }
            
        };

        if let Err(e) = conn.execute("UPDATE todos SET done = 0 WHERE id = ?", params![valid_id]) {
            println!("Failed to mark todo as not done: {}", e);
            return;
        }
        println!("Marked todo item with ID: {} as not done.", valid_id);
    }



}



#[derive(Parser)]
#[command(name = "Todo CLI App")]
#[command(version = "1.0.0")]
#[command(about = "A simple todo CLI app", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Add {
        item: String,
    },
    List,
    Done {
        id: i32,
    },
    Undone {
        id: i32,
    },
    Remove {
        id: i32,
    },
    Clear,
}


fn main() {
    let cli = Cli::parse();
    let mut app = TodoApp::default();

    match cli.command {
        Commands::Add { item } => app.add_todo(&item),
        Commands::List => app.list_todos(),
        Commands::Done { id } => app.mark_as_done(id),
        Commands::Undone { id } => app.mark_as_not_done(id),
        Commands::Remove { id } => app.remove_todo(id),
        Commands::Clear => app.clear_all(),
        // If no subcommand is provided, list todos by default
        // But since clap requires a subcommand, we need to make it optional:
        // So, change `command: Commands` to `command: Option<Commands>` in Cli,
        // and handle None here:
    }
}

// to run you now need to use cargo run -- <subcommand> [args]
// e.g., cargo run -- add "Buy groceries"