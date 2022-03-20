import config
from xmlrpc.client import ServerProxy, Error

def menu():
    print("Available options:")
    print("1) Create note")
    print("2) Get notes of a topic")
    print("3) Append data to topic")
    print("0) Exit")

    try:
        return int(input("Your choice: "))
    except ValueError:
        return -1


def main():
    choice = -1
    s = ServerProxy(f"http://{config.HOST}:{config.PORT}")

    while True:
        choice = menu()

        match choice:
            case 0:
                break
            case 1:
                topic = input("Topic name: ")
                text = input("Note description: ")
                s.insert(topic, text)
            case 2:
                topic = input("Topic name: ")
                topics = s.find(topic)

                if (len(topics) == 0):
                    print("No notes found.")
                else:
                    print("Notes found:")

                # print notes
                for t in topics:
                    print(f"Note: {t[0]}")
            case 3:
                searchTerm = input("Search term: ")
                topic = input("Topic name: ")
                res = s.enrich(topic, searchTerm)
                print((res and "Data appended.") or "Could not append data.")

            case _:
                print("Invalid option. Try again.")

        print()

    print("Exiting...")


main()
