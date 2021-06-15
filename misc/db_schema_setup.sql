CREATE TABLE document (id SERIAL PRIMARY KEY,
                       created_date date,
                       document_text text,
                       rubrics_array text);

CREATE INDEX document_dates_desc_idx ON document(created_date); 