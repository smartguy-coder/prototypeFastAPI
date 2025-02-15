from connection_config import get_connection
from consumer import consume_messages


def main():
    with get_connection() as connection:
        print("*" * 80)
        with connection.channel() as channel:
            consume_messages(channel=channel)


if __name__ == "__main__":
    main()
