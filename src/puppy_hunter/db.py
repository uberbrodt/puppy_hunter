import sqlite3
import json
import time


def initialize_db(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute(
        "create table puppies(id, name, detail_link, sex, breed, size, stage, updated_at)"
    )
    conn.close()


def get_updated_since(db_name, time):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    puppies = conn.execute(
        "select * from puppies WHERE updated_at >= :updated_at", {"updated_at": time}
    )
    return puppies


def update_batch(db_name, puppy_filename):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row

    current_time = int(time.time())

    with open(puppy_filename, "r") as f:
        puppies = json.loads(f.read())

    for pupper in puppies:
        cur = conn.execute("select * from puppies WHERE id = :id", {"id": pupper["id"]})

        result = cur.fetchone()

        if result is None:
            print(f"Adding new pupper to puppy db! {pupper['id']}")
            conn.execute(
                """insert into
                puppies(id, name, detail_link, sex, breed, size, stage, updated_at)
                VALUES(:id, :name, :detail_link, :sex, :breed, :size, :stage, :updated_at)
                """,
                {
                    "id": pupper["id"],
                    "name": pupper["name"],
                    "detail_link": pupper["detail_link"],
                    "sex": pupper["sex"],
                    "breed": pupper["breed"],
                    "size": pupper["size"],
                    "stage": pupper["stage"],
                    "updated_at": current_time,
                },
            )

        else:
            if result["stage"] != pupper["stage"]:
                print(
                    f"Updating pupper stage in puppy db! {pupper['id']} - {pupper['stage']}"
                )
                conn.execute(
                    "update puppies SET stage = :stage, updated_at = :updated_at WHERE id = :id",
                    {
                        "stage": pupper["stage"],
                        "updated_at": current_time,
                        "id": pupper["id"],
                    },
                )
    conn.commit()
    print("Puppy Hunter DB update batch completed!")
    conn.close()
