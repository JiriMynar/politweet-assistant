/**
 * Vylepšené nahrávání obrázků pro politweet-assistant
 * 
 * Tento soubor obsahuje JavaScript kód pro vylepšení funkce nahrávání obrázků:
 * - Progress bar pro zobrazení průběhu nahrávání
 * - Náhled obrázku před analýzou s možností ořezu
 * - Vylepšená podpora pro drag & drop a Ctrl+V
 * - Informace o maximální velikosti a podporovaných formátech
 * 
 * Jak implementovat:
 * 1. Přidejte tento soubor do adresáře static/js/
 * 2. Přidejte odkaz na tento soubor v base.html
 * 3. Ujistěte se, že máte odpovídající HTML elementy s uvedenými ID
 */

document.addEventListener('DOMContentLoaded', function() {
    // Konfigurace
    const config = {
        maxFileSize: 5 * 1024 * 1024, // 5MB
        allowedFormats: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        dropZoneId: 'dropZone',
        imagePreviewId: 'imagePreview',
        progressBarId: 'uploadProgressBar',
        progressContainerId: 'uploadProgressContainer',
        imageInputId: 'imageInput',
        clearButtonId: 'clearImageButton',
        cropButtonId: 'cropImageButton',
        errorMessageId: 'uploadErrorMessage',
        infoMessageId: 'uploadInfoMessage'
    };

    // Získání referencí na DOM elementy
    const dropZone = document.getElementById(config.dropZoneId);
    const imagePreview = document.getElementById(config.imagePreviewId);
    const progressBar = document.getElementById(config.progressBarId);
    const progressContainer = document.getElementById(config.progressContainerId);
    const imageInput = document.getElementById(config.imageInputId);
    const clearButton = document.getElementById(config.clearButtonId);
    const cropButton = document.getElementById(config.cropButtonId);
    const errorMessage = document.getElementById(config.errorMessageId);
    const infoMessage = document.getElementById(config.infoMessageId);

    // Proměnné pro ořezávání
    let cropper = null;
    let isCropping = false;

    // Zobrazení informací o nahrávání
    if (infoMessage) {
        infoMessage.textContent = `Podporované formáty: JPG, PNG, GIF, WebP. Maximální velikost: 5MB.`;
    }

    // Inicializace událostí pro drag & drop
    if (dropZone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropZone.classList.add('border-blue-500', 'bg-blue-50');
        }

        function unhighlight() {
            dropZone.classList.remove('border-blue-500', 'bg-blue-50');
        }

        // Zpracování upuštěného souboru
        dropZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                handleFiles(files);
            }
        }
    }

    // Zpracování vložení obrázku pomocí Ctrl+V
    document.addEventListener('paste', function(e) {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const file = items[i].getAsFile();
                handleFiles([file]);
                break;
            }
        }
    });

    // Zpracování výběru souboru přes input
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFiles(this.files);
            }
        });
    }

    // Zpracování souborů
    function handleFiles(files) {
        const file = files[0];
        
        // Kontrola typu souboru
        if (!config.allowedFormats.includes(file.type)) {
            showError('Nepodporovaný formát souboru. Povolené formáty jsou: JPG, PNG, GIF, WebP.');
            return;
        }
        
        // Kontrola velikosti souboru
        if (file.size > config.maxFileSize) {
            showError('Soubor je příliš velký. Maximální velikost je 5MB.');
            return;
        }
        
        // Skrytí chybové zprávy, pokud existuje
        if (errorMessage) {
            errorMessage.textContent = '';
            errorMessage.classList.add('hidden');
        }
        
        // Zobrazení náhledu
        previewFile(file);
        
        // Simulace nahrávání s progress barem
        simulateUpload();
    }

    // Zobrazení náhledu souboru
    function previewFile(file) {
        if (!imagePreview) return;
        
        // Odstranění předchozího náhledu a cropperu
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        
        const reader = new FileReader();
        
        reader.onloadstart = function() {
            // Zobrazení progress containeru, pokud existuje
            if (progressContainer) {
                progressContainer.classList.remove('hidden');
            }
        };
        
        reader.onload = function(e) {
            // Nastavení náhledu
            imagePreview.src = e.target.result;
            imagePreview.classList.remove('hidden');
            
            // Zobrazení tlačítek pro manipulaci s obrázkem
            if (clearButton) clearButton.classList.remove('hidden');
            if (cropButton) cropButton.classList.remove('hidden');
        };
        
        reader.readAsDataURL(file);
    }

    // Simulace nahrávání s progress barem
    function simulateUpload() {
        if (!progressBar) return;
        
        let width = 0;
        progressBar.style.width = '0%';
        
        const interval = setInterval(function() {
            if (width >= 100) {
                clearInterval(interval);
                // Skrytí progress baru po dokončení
                setTimeout(function() {
                    if (progressContainer) {
                        progressContainer.classList.add('hidden');
                    }
                }, 500);
            } else {
                width += 5;
                progressBar.style.width = width + '%';
                progressBar.textContent = width + '%';
            }
        }, 100);
    }

    // Zobrazení chybové zprávy
    function showError(message) {
        if (!errorMessage) return;
        
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }

    // Vymazání obrázku
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            clearImage();
        });
    }

    function clearImage() {
        if (imagePreview) {
            imagePreview.src = '';
            imagePreview.classList.add('hidden');
        }
        
        if (imageInput) {
            imageInput.value = '';
        }
        
        if (clearButton) {
            clearButton.classList.add('hidden');
        }
        
        if (cropButton) {
            cropButton.classList.add('hidden');
        }
        
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        
        isCropping = false;
    }

    // Ořezání obrázku
    if (cropButton) {
        cropButton.addEventListener('click', function() {
            toggleCropper();
        });
    }

    function toggleCropper() {
        if (!imagePreview || !imagePreview.src) return;
        
        if (isCropping) {
            // Aplikace ořezu
            const canvas = cropper.getCroppedCanvas();
            if (canvas) {
                imagePreview.src = canvas.toDataURL();
                
                // Převod na Blob pro pozdější odeslání
                canvas.toBlob(function(blob) {
                    // Zde můžete uložit blob pro pozdější odeslání
                    console.log('Obrázek oříznut a připraven k odeslání');
                });
            }
            
            cropper.destroy();
            cropper = null;
            isCropping = false;
            
            if (cropButton) {
                cropButton.textContent = 'Oříznout obrázek';
            }
        } else {
            // Inicializace cropperu
            cropper = new Cropper(imagePreview, {
                aspectRatio: NaN,
                viewMode: 1,
                guides: true,
                background: true,
                autoCropArea: 0.8,
                responsive: true
            });
            
            isCropping = true;
            
            if (cropButton) {
                cropButton.textContent = 'Použít ořez';
            }
        }
    }
});

/**
 * Poznámka: Tento kód vyžaduje knihovnu Cropper.js pro funkci ořezávání obrázků.
 * Přidejte následující řádky do base.html:
 * 
 * <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css">
 * <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js"></script>
 * 
 * Také je potřeba přidat následující HTML elementy do index.html:
 * 
 * <!-- Progress bar pro nahrávání -->
 * <div id="uploadProgressContainer" class="hidden w-full h-2 bg-gray-200 rounded-full mt-2 mb-4">
 *   <div id="uploadProgressBar" class="h-full text-xs text-center text-white bg-blue-500 rounded-full" style="width: 0%"></div>
 * </div>
 * 
 * <!-- Informace o nahrávání -->
 * <p id="uploadInfoMessage" class="text-sm text-gray-600 mt-1"></p>
 * 
 * <!-- Chybová zpráva -->
 * <p id="uploadErrorMessage" class="text-sm text-red-600 mt-1 hidden"></p>
 * 
 * <!-- Náhled obrázku -->
 * <div class="relative mt-4">
 *   <img id="imagePreview" class="max-w-full max-h-64 hidden" alt="Náhled obrázku">
 * </div>
 * 
 * <!-- Tlačítka pro manipulaci s obrázkem -->
 * <div class="flex space-x-2 mt-2">
 *   <button id="cropImageButton" class="px-3 py-1 bg-blue-500 text-white rounded-md hidden">Oříznout obrázek</button>
 *   <button id="clearImageButton" class="px-3 py-1 bg-red-500 text-white rounded-md hidden">Odstranit obrázek</button>
 * </div>
 */
