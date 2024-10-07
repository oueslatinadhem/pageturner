
// Fonction pour afficher une boîte de dialogue modale
function showModal(title, detail, isEdit = false, id = null) {
  // suppression des anciennes boites de dialogue
  [...document.getElementsByTagName('dialog')].forEach((element) => element.remove());
  // Création de la boîte de dialogue
  const dialog = document.createElement('dialog');
  dialog.id = 'myDialog';
  // Contenu de la boîte de dialogue
  const content = document.createElement('div');
  content.innerHTML = `
    <h2>${title}</h2>
    <p>${detail}</p>
  `;
  // Si c'est un mode édition, on remplace le contenu par un formulaire
  if (isEdit) {
    content.innerHTML = `
      <form id="editForm">
        <input type="hidden" name="id" value="${id}">
        <label for="title">Titre:</label><br>
        <input type="text" id="title" name="titre" value="${title}"><br>
        <label for="detail">Détail:</label><br>
        <textarea id="detail" name="detail">${detail}</textarea>
      </form>
    `;
  }
  // Ajout des boutons
  const buttons = document.createElement('div');
  buttons.classList.add('buttons');
  if (isEdit) {
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Enregistrer';
    saveButton.addEventListener('click', () => {
      const formData = new FormData(document.getElementById('editForm'));
      const data = Object.fromEntries(formData.entries());
      dialog.close();
      if (data.id=='null') 
        sendRequest('POST', `${APIUrl}/${id}`, data)
      else
        sendRequest('PUT', `${APIUrl}/${id}`, data)
    
      // Ici, vous pouvez faire ce que vous voulez avec les données, par exemple les envoyer à un serveur
      fetchData();
    });
    buttons.appendChild(saveButton);
  }
  const closeButton = document.createElement('button');
  closeButton.textContent = 'Fermer';
  closeButton.addEventListener('click', () => {
    dialog.close();
  });
  buttons.appendChild(closeButton);

  // Ajout du contenu et des boutons à la boîte de dialogue
  dialog.appendChild(content);
  dialog.appendChild(buttons);

  // Ajout de la boîte de dialogue au document
  document.body.appendChild(dialog);

  // Ouverture de la boîte de dialogue
  dialog.showModal();
}
// Fonction pour envoyer une requête AJAX
async function sendRequest(method, url, data) {
  const response = await fetch(url, {
    method: method,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return response.json();
}

// Événement au clic sur le bouton "Ajouter"
document.getElementById('add-button').addEventListener('click', () => {
  showModal('', '', true, null);
});

// Événements pour les boutons "Détail", "Modifier" et "Supprimer"
function handleButton(event) {
  const action = event.target.dataset.action;
  const id = event.target.dataset.id;
  if (action === 'detail') {
    // Afficher les détails de l'élément
    sendRequest('GET', `${APIUrl}/${id}`)
      .then(data => {
        data=JSON.parse(data);
        showModal(data.titre, data.detail, false, id);
      });
  } else if (action === 'edit') {
    // Afficher le formulaire de modification
    sendRequest('GET', `${APIUrl}/${id}`)
      .then(data => {
        data=JSON.parse(data);
       showModal(data.titre, data.detail, true, id);
      });
  } else if (action === 'delete') {
    // Confirmer la suppression
    if (confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
      sendRequest('DELETE', `${APIUrl}/${id}`);
      fetchData(); // Rafraîchir la liste
    }
  }
}


// Récupérer les données depuis le serveur
async function fetchData() {
  const response = await sendRequest('GET', APIUrl);
  let data = await response;
  if (data=="") data={};
  data=JSON.parse(data);
  // Mettre à jour le tableau HTML avec les données reçues
  const tableBody = document.getElementById('data-table');
  tableBody.innerHTML = '';
  data.forEach(item => {
    // Créer une ligne de tableau pour chaque élément
    const row = document.createElement('tr');
    const titre= document.createElement('td');
    titre.textContent=item.titre;
    row.appendChild(titre);
    let col = document.createElement('td');
    let bt=document.createElement('div');
    bt.className='button';
    bt.dataset.action='detail';
    bt.dataset.id=item.id;
    bt.innerHTML='🔍<br><span class="tooltip">détails</span>';
    bt.addEventListener('click',handleButton);
    col.appendChild(bt);
    row.appendChild(col);
    col = document.createElement('td');
    bt=document.createElement('div');
    bt.className='button';
    bt.dataset.action='edit';
    bt.dataset.id=item.id;
    bt.innerHTML='🖊️<br><span class="tooltip">modifier</span>';
    bt.addEventListener('click',handleButton);
    col.appendChild(bt);
    row.appendChild(col);
    col = document.createElement('td');
    bt=document.createElement('div');
    bt.className='button';
    bt.dataset.action='delete';
    bt.dataset.id=item.id;
    bt.innerHTML='🗑️<br><span class="tooltip">supprimer</span>';
    bt.addEventListener('click',handleButton);
    col.appendChild(bt);
    row.appendChild(col);
    tableBody.appendChild(row);
  });
}



// Fonction pour gérer la soumission du formulaire
function handleSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const data = {
    titre: form.titre.value,
    detail: form.detail.value
  };
  const id = form.id.value; // Si présent (pour les mises à jour)
  if (id) {
    // Mise à jour
    sendRequest('PUT', `${APIUrl}/${id}`, data)
      .then(() => {
        fetchData();
        closeModal();
      });
  } else {
    // Création
    sendRequest('POST', APIUrl, data)
      .then(() => {
        fetchData();
        closeModal();
      });
  }
}

// Appeler la fonction pour récupérer les données initiales
fetchData();