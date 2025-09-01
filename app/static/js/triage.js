let selectedImages = [];

        // Adicionar event listeners para cada imagem
        document.querySelectorAll('.image-item').forEach(item => {
            item.addEventListener('click', function () {
                const imageId = this.getAttribute('data-id');
                const imageDescription = this.getAttribute('data-description');

                if (this.classList.contains('selected')) {
                    // Deselecionar
                    this.classList.remove('selected');
                    selectedImages = selectedImages.filter(img => img.id !== imageId);
                } else {
                    // Selecionar
                    this.classList.add('selected');
                    selectedImages.push({
                        id: imageId,
                        name: imageDescription
                    });
                }

                updateCounter();
                updateHiddenField();
            });
        });

        function updateCounter() {
            const countElement = document.getElementById('count');
            countElement.textContent = selectedImages.length;

            // Animar o contador
            countElement.style.transform = 'scale(1.2)';
            setTimeout(() => {
                countElement.style.transform = 'scale(1)';
            }, 200);
        }

        function updateHiddenField() {
            // Atualizar o campo hidden com os IDs das imagens selecionadas
            const hiddenField = document.getElementById('selectedImages');
            hiddenField.value = JSON.stringify(selectedImages);
        }

        function handleSubmit(event) {
            event.preventDefault();

            if (selectedImages.length === 0) {
                alert('Por favor, selecione pelo menos uma imagem antes de enviar.');
                return;
            }

            // Mostrar dados que seriam enviados
            console.log('Imagens selecionadas:', selectedImages);
            alert(`Formulário enviado!\nImagens selecionadas: ${selectedImages.length}\nDescrição: ${selectedImages.map(img => img.name).join(', ')}`);

            // Enviando descrição das imagens para o Servidor.
            fetch('/api/triage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    selectedImages: selectedImages
                }),
            })
                .then(response => response.json())
                .then(data => {
                    // DEBUG: Mostrar a resposta do servidor
                    // console.log('Success:', data);

                    // Redirecionar para a URL fornecida na resposta
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });

                
        }