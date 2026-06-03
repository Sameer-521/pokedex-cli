import asyncio
import csv
import httpx

ABILITY_LIST_URL = "https://pokeapi.co/api/v2/ability?limit=1000"
CONCURRENCY = 20
OUTPUT = "abilities.csv"


async def fetch_ability(
    client: httpx.AsyncClient, sem: asyncio.Semaphore, url: str
) -> dict:
    async with sem:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    eng_entries = [
        e for e in data["flavor_text_entries"] if e["language"]["name"] == "en"
    ]
    if eng_entries:
        desc = eng_entries[0]["flavor_text"].replace("\n", " ").replace("\f", " ")
    else:
        desc = ""

    return {"id": data["id"], "name": data["name"], "description": desc}


async def main() -> None:
    sem = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(ABILITY_LIST_URL)
        r.raise_for_status()
        results = r.json()["results"]

        tasks = [fetch_ability(client, sem, item["url"]) for item in results]
        abilities = await asyncio.gather(*tasks)

    abilities.sort(key=lambda x: x["id"])

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "description"])
        writer.writeheader()
        writer.writerows(abilities)

    print(f"Downloaded {len(abilities)} abilities to {OUTPUT}")


if __name__ == "__main__":
    asyncio.run(main())
