create or replace view vw_zaw2_component_load as
select
    bc.codice_componente,
    'ZAW-2' as postazione_critica,
    count(distinct bc.articolo) as numero_articoli_coinvolti,
    sum(coalesce(cd.quantita,0)) as domanda_totale,
    string_agg(
        bc.articolo || ':' || coalesce(cd.quantita,0),
        ' | '
        order by bc.articolo
    ) as dettaglio_domanda
from bom_components bc
left join customer_demand cd
    on cd.articolo = bc.articolo
where upper(coalesce(bc.postazione,'')) in (
    'ZAW2',
    'ZAW-2',
    'ZAW 2'
)
group by
    bc.codice_componente;
