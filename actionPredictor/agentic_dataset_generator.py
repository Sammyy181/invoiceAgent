import random
import json

# Valid chatbot-executable actions
VALID_ACTIONS = [
    "open_editor",
    "add_service",
    "close_editor",
    "view_last_invoice",
    "list_services",
    "view_current_invoice",
    "copy_previous_data",
    "list_customers",
    "add_customer",
    "edit_customer",
    "update_tax"
]

# Actual valid pages in your app
PAGES = [
    "select_service",
    "select_customer"
]

# Realistic prior action chains for each action
REALISTIC_WORKFLOWS = [
    ["open_editor", "list_services", "add_service", "add_customer", "add_customer", "update_tax", "view_current_invoice", "close_editor"],
    ["open_editor", "list_services", "view_last_invoice", "edit_customer", "copy_previous_data", "view_current_invoice", "close_editor"],
    ["open_editor", "list_services", "add_service", "add_customer", "edit_customer", "update_tax", "view_current_invoice", "close_editor"],
    ["open_editor", "list_services", "add_service", "copy_previous_data", "update_tax", "close_editor"],
    ["open_editor", "list_services", "view_last_invoice", "view_current_invoice", "close_editor"],
    ["open_editor", "add_service", "edit_customer", "close_editor"],
    ["open_editor", "view_last_invoice", "update_tax", "close_editor"],
    ["open_editor", "list_services", "add_service", "list_customers", "edit_customer", "add_customer", "copy_previous_data", "view_current_invoice", "close_editor"]
]


def generate_agentic_data_entry():
    workflow = random.choice(REALISTIC_WORKFLOWS)
    action_index = random.randint(1, len(workflow) - 1)  # avoid index 0 to ensure history exists
    action = workflow[action_index]
    history = workflow[max(0, action_index - 3):action_index]

    # Pad to always have 3 history features
    padded = [None] * (3 - len(history)) + history

    return {
        "current_page": random.choice(["select_service", "select_customer"]),
        "last_action_1": padded[0],
        "last_action_2": padded[1],
        "last_action_3": padded[2],
        "action": action
    }


# Generate full dataset
def generate_dataset(n=1000, save_path="agentic_chatbot_dataset_v3.jsonl"):
    with open(save_path, "w") as f:
        for _ in range(n):
            row = generate_agentic_data_entry()
            f.write(json.dumps(row) + "\n")
    print(f"✅ Dataset saved to {save_path}")

# If running this script directly
if __name__ == "__main__":
    generate_dataset(n=2000)
