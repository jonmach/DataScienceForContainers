FROM postgres:11.5

COPY pg-setup.sql /docker-entrypoint-initdb.d/

EXPOSE 5432

CMD ["postgres"]



