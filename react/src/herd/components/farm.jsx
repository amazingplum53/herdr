
export default function FarmDisplay({ farm }) {
  return (
    <header>
      <h2>{farm.name}</h2>

      {farm.address_line_1 && <p>{farm.address_line_1}</p>}
      {farm.postcode && <p>{farm.postcode}</p>}
      {farm.country && <p>{farm.country}</p>}
      {farm.animal_count !== undefined && (
        <p>Animals: {farm.animal_count}</p>
      )}
    </header>
  );
}