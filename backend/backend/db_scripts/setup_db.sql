BEGIN;


CREATE TABLE IF NOT EXISTS public.parcelle
(
    id serial NOT NULL,
    nom text COLLATE pg_catalog."default" NOT NULL,
    region polygon,
    CONSTRAINT parcelle_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.rang
(
    id serial NOT NULL,
    id_parcelle serial NOT NULL,
    p0 point NOT NULL,
    p1 point NOT NULL,
    CONSTRAINT rang_pkey PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.rang
    ADD CONSTRAINT rang_id_parcelle_fkey FOREIGN KEY (id_parcelle)
    REFERENCES public.parcelle (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

END;