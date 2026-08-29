
from mongo.client import get_client


def main():
    client = get_client()
    client.init_db()


if __name__ == "__main__":
    main()

