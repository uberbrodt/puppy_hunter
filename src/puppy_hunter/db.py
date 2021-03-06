import sqlite3
import json
import time
import puppy_hunter.log

logger = puppy_hunter.log.get_logger()


def initialize_db(db_name):
    conn = sqlite3.connect(db_name)
    conn.execute(
        "create table puppies(id, name, detail_link, sex, breed, size, stage, updated_at, notified_since_update)"
    )
    conn.close()


def get_unnotified_puppies(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    puppies = conn.execute("select * from puppies where notified_since_update = 0")

    return puppies


def mark_puppies_notified(db_name, puppy_ids):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row

    sql_base = "update puppies SET notified_since_update = 1 where id IN ({})"
    sql = sql_base.format(", ".join("?" * len(puppy_ids)), puppy_ids)
    conn.execute(sql, puppy_ids)
    conn.commit()
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
            logger.info(f"Adding new pupper to puppy db! {pupper['id']}")
            conn.execute(
                """insert into
                puppies(id, name, detail_link, sex, breed, size, stage, updated_at, notified_since_update)
                VALUES(:id, :name, :detail_link, :sex, :breed, :size, :stage, :updated_at, 0)
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
                logger.info(
                    f"Updating pupper stage in puppy db! {pupper['id']} - {pupper['stage']}"
                )
                conn.execute(
                    """
                    update puppies
                    SET
                        stage = :stage,
                        updated_at = :updated_at,
                        notified_since_update = 0
                    WHERE id = :id
                    """,
                    {
                        "stage": pupper["stage"],
                        "updated_at": current_time,
                        "id": pupper["id"],
                    },
                )
    conn.commit()
    logger.info("Puppy Hunter DB update batch completed!")
    conn.close()
