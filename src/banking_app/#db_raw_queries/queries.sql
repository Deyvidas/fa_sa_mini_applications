SELECT status_desc.description
  FROM status_desc
       INNER JOIN clients
               ON status_desc.status = clients.status
              AND clients.phone LIKE '9864949005';

