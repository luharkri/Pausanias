struct Task {
    description: String,
    done: bool,
}

impl Task {
    fn new(description: String) -> Task {
        Task {
            description,
            done: false,
        }
    }

    fn mark_done(&mut self) {
        self.done = true;
    }

    fn display(&self) {
        let status = if self.done { "✔️" } else { "❌" };
        println!("{} - {}", status, self.description);
    }
}

use std::env;

use std::fs::{OpenOptions, read_to_string, write};

fn add_task(description: String) {
    let mut tasks = load_tasks();
    tasks.push(Task::new(description));
    save_tasks(&tasks);
}

fn list_tasks() {
    let tasks = load_tasks();
    for task in tasks {
        task.display();
    }
}

fn mark_done(description: String) {
    let mut tasks = load_tasks();
    let mut found: bool = false;
    for task in &mut tasks {
        if task.description == description {
            task.mark_done();
            found = true;
        }
    }
    save_tasks(&tasks);
    if found == false{
        println!("Task Does Not Exist");
    }
    else{
        println!("Marked Done");
    }
}




fn load_tasks() -> Vec<Task> {
    let content = read_to_string("tasks.txt").unwrap_or_else(|_| String::new());
    let mut tasks = Vec::new();
    for line in content.lines() {
        let parts: Vec<&str> = line.split('\t').collect();
        if parts.len() == 2 {
            let task = Task {
                description: parts[0].to_string(),
                done: parts[1] == "done",
            };
            tasks.push(task);
        }
    }
    tasks
}

fn save_tasks(tasks: &[Task]) {
    let mut content = String::new();
    for task in tasks {
        let status = if task.done { "done" } else { "not done" };
        content.push_str(&format!("{}\t{}\n", task.description, status));
    }
    write("tasks.txt", content).expect("Unable to write file");
}


fn main() {
    let args: Vec<String> = env::args().collect();
    let command = &args[1];
    let description = args.get(2).unwrap_or(&String::new()).clone();

    // Match the command and call corresponding functions
    match command.as_str() {
        "add" => add_task(description),
        "list" => list_tasks(),
        "done" => mark_done(description),
        _ => println!("Unknown command. Use 'add', 'list', or 'done'."),
    }
}