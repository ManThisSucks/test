import os
import pickle


class ItemCounter:
    def __init__(self, name: str, quantity: int):
        self.name = name
        self.quantity = quantity

    def __str__(self):
        return f"{self.name} ({self.quantity})"

    def __repr__(self):
        return self.__str__()

    def add_units(self, quantity=1):
        self.quantity += quantity

    def take_items(self, quantity=1):
        if self.quantity < quantity:
            print("Quantity ")
        self.quantity -= quantity

    def is_sold_out(self):
        return self.quantity < 1

    def set_quantity(self, quantity):
        self.quantity = quantity


class Inventory:
    def __init__(self, name=""):
        self.items = list()
        self.item_names = list()
        self.name = name
        self.history = list()

    def __getitem__(self, item_name):
        if self.has(item_name):
            ind = self.item_names.index(item_name.lower())
            return self.items[ind]

    def populate(self, counters):
        if self.item_names:
            print("Can only populate empty inventory; nothing happened")
            return
        for counter in counters:
            self.add_item(counter.name, counter.quantity, incognito=True)
        self.history.append("populate")

    def has(self, item_name):
        return item_name.lower() in self.item_names

    def add_item(self, item_name, quantity=1, incognito=False):
        if self.has(item_name):
            self[item_name].add_units(quantity)
            if not incognito:
                self.history.append(("add", (item_name, quantity)))
        else:
            self.items.append(ItemCounter(item_name, quantity))
            self.item_names.append(item_name.lower())
            if not incognito:
                self.history.append(("create", (item_name, quantity)))

    def take_item(self, item_name, quantity=1, incognito=False):
        if not self.has(item_name):
            raise NameError("item not found in inventory")
        item = self[item_name]
        stock = item.quantity
        if stock < quantity:
            print(
                f"# Tried to take {quantity} from {item.name} but current recorded stock was {stock}; set stock to 0"
            )
            quantity = stock
        self[item_name].take_items(quantity)

        if not incognito:
            self.history.append(("take", (item_name, quantity)))

    def remove_item(self, item_name, incognito=False):
        if self.has(item_name):
            ind = self.item_names.index(item_name.lower())
            quantity = self.items[ind].quantity
            self.item_names.pop(ind)
            self.items.pop(ind)

            if not incognito:
                self.history.append(("remove", (item_name, quantity)))

    def is_empty(self):
        return not bool(self.item_names)

    def undo(self):
        if not self.history:
            print("Nothing to undo")
            return
        last_action = self.history.pop()

        if last_action == "populate":
            self.items = list()
            self.item_names = list()
            return "populate"

        command = last_action[0]
        name = last_action[1][0]
        quantity = last_action[1][1]

        if command == "add":
            self.take_item(name, quantity, incognito=True)

        elif command == "create":
            self.remove_item(name, incognito=True)

        elif command == "take":
            self.add_item(name, quantity, incognito=True)

        elif command == "remove":
            self.add_item(name, quantity, incognito=True)

        return command, quantity, name

    def export(self, filename):
        if filename[-4:] == ".inv":
            filename = filename[:-4]
        path = f"inventories/{filename}.inv"
        try:
            if os.path.exists(path):
                os.remove(path)
            pickle.dump(self, open(path, "wb"))
        except FileNotFoundError:
            os.mkdir("inventories")
            pickle.dump(self, open(path, "wb"))

    def __repr__(self):
        header = f"Inventory{' ' if self.name else ''}{self.name}:\n"
        if self.is_empty():
            body = "\t(empty)"
        else:
            body = "\n".join([f"\t{item.name}: {item.quantity}" for item in self.items])
        return header + body


def import_inv(filename):
    if not filename[-4:] == ".inv":
        filename = filename + ".inv"
    return pickle.load(open("inventories/" + filename, "rb"))


if __name__ == "__main__":
    os.system("title Inventory Prototype")
    os.system("color f0")
    inventory = Inventory()
    helptext = (
        "Available commands:",
        '"add [qty] [item]" to add an item/items to inventory',
        '"take [qty] [item]" to take out an item/items from inventory',
        '"remove [item]" to delete an item from the listing',
        '"show" to display the inventory',
        '"auto" to toggle automatic displaying of inventory after commands',
        '"undo" to undo the previous inventory command',
        '"export [filename]" to export the current inventory to a file',
        '"import [filename]" to import an existing inventory',
        '"clear" to clear the screen (does not affect inventory)',
        '"exit" to exit',
    )

    def parse_command(command):
        if isinstance(command, str):
            command = command.split()

        action = command[0].lower()
        if action not in [
            "add",
            "take",
            "remove",
            "undo",
            "show",
            "auto",
            "help",
            "?",
            "export",
            "clear",
            "import",
            "exit",
        ]:
            raise ValueError("invalid keyword")

        if action == "add":
            if len(command) < 3:
                raise ValueError("expected 3 keywords")
            quantity = command[1]
            if not quantity.isdigit():
                raise ValueError("expected 2nd keyword to be number")
            name = " ".join(command[2:])
            return "add", int(quantity), name

        if action == "take":
            if len(command) < 3:
                raise ValueError("expected 3 keywords")
            quantity = command[1]
            if not quantity.isdigit():
                raise ValueError("expected 2nd keyword to be number")
            name = " ".join(command[2:])
            return "take", int(quantity), name

        if action == "remove":
            if len(command) < 2:
                raise ValueError("expected 2 keywords")
            name = " ".join(command[1:])
            return "remove", name

        if action == "export":
            if len(command) != 2:
                raise ValueError("expected 2 keywords")
            name = command[1]
            return "export", name

        if action == "import":
            if len(command) != 2:
                raise ValueError("expected 2 keywords")
            name = command[1]
            return "import", name

        return action, None  # catch-all for 1-word commands

    auto = False
    print("--------------------------------------------------")
    print("Welcome to the inventory system text UI prototype!")
    print('To display available commands, type "help" or "?".')
    print("--------------------------------------------------")

    if os.path.exists("inventories/latest.inv"):
        print("\nWould you like to restore your last saved inventory? (Y/N)")
        while True:
            restore = input(">>>").upper()
            if restore == "Y":
                inventory = import_inv("latest")
                os.remove("inventories/latest.inv")
                break
            elif restore == "N":
                break

    elif os.path.exists("inventories/autosave.inv"):
        print(
            "\nClean save file was not detected. Would you like to restore your last autosaved inventory? (Y/N)"
        )
        while True:
            restore = input(">>>").upper()
            if restore == "Y":
                inventory = import_inv("autosave")
                break
            elif restore == "N":
                break

    while True:
        print()
        try:
            user_command = parse_command(input(">>>"))
        except ValueError as e:
            print(e)
            continue
        kw = user_command[0]
        print()

        try:
            if kw == "add":
                q = user_command[1]
                n = " ".join(user_command[2:])

                print(f"Adding {q} {n} to inventory...")
                inventory.add_item(n, q)
                inventory.export("autosave")

            elif kw == "take":
                q = user_command[1]
                n = " ".join(user_command[2:])

                print(f"Removing {q} {n} from inventory...")
                if n.lower() not in inventory.item_names:
                    print(f"{n} not found in inventory")
                else:
                    inventory.take_item(n, q)
                    inventory.export("autosave")

            elif kw == "remove":
                n = " ".join(user_command[1:])

                print(f"removing {n} from inventory listing...")
                if n.lower() not in inventory.item_names:
                    print(f"{n} not found in inventory")
                else:
                    inventory.remove_item(n)
                    inventory.export("autosave")

            elif kw == "undo":
                print(f"Undoing previous inventory command...")
                a, q, n = inventory.undo()
                print(f"Undid inventory command ({a}: {q}x {n})")

            elif kw == "show":
                print(inventory)
                continue

            elif kw == "auto":
                auto = not auto
                if auto:
                    print("Automatic inventory display is now enabled")
                else:
                    print("Automatic inventory display is now disabled")

            elif kw in ["?", "help"]:
                print(*helptext, sep="\n")
                continue

            elif kw == "export":
                n = user_command[1]
                inventory.export(n)
                print(f"Exported current inventory as {n}")

            elif kw == "clear":
                os.system("cls")
                continue

            elif kw == "import":
                n = user_command[1]
                try:
                    i = import_inv(n)
                except FileNotFoundError:
                    print("Could not find file to import")
                else:
                    inventory = i
                    print(f"Successfully imported {n}")

            elif kw == "exit":
                confirmation = input("Are you sure you want to exit? (Y)\n>>>")
                if confirmation.upper() == "Y":
                    print("Saving...")
                    inventory.export("latest")
                    print("Done!")
                    os.system("pause")
                    break
                else:
                    print("reversing exit command...")

            if auto:
                print(inventory)

        except Exception as e:
            print("Ran into unexpected error; please restart as soon as possible")
            print(e)
