export default async function MyNextFastAPIApp() {
  const role = await fetchEngineerRole();

  return (
    <>
      <div>{`The main skill of a ${role}`}</div>
    </>
  );
}

async function fetchEngineerRole() {
 
  const baseUrl = "http://localhost:3000";

  try { 
    const response = await fetch(
      `${baseUrl}/api/py`
    );
    if (!response.ok) {
      throw new Error("Failed to fetch data");
    }
    const role = await response.json();
    return role;
  } catch (error) {

    console.error("Error fetching engineer role:", error);
    return null;
  }
}