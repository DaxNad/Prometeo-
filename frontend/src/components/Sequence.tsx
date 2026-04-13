type Props = {
  sequence: any[];
};

export default function Sequence({ sequence }: Props) {

  if (!sequence || sequence.length === 0)
    return <div>nessuna sequenza</div>;

  return (

    <section>

      <h2>sequenza consigliata</h2>

      {sequence.map((item, i) => (

        <div key={i}>

          {item.article} → {item.critical_station}

        </div>

      ))}

    </section>

  );

}
