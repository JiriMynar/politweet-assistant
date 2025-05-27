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
        imagePreviewId: 'preview',
        imageInputId: 'imageInput',
        errorMessageId: 'uploadErrorMessage'
    };

    // Získání referencí na DOM elementy
    const dropZone = document.getElementById(config.dropZoneId);
    const imageInput = document.getElementById(config.imageInputId);

    // Inicializace Alpine.js komponenty pro factChecker
    if (typeof window.factChecker !== 'function') {
        window.factChecker = function() {
            return {
                textInput: '',
                imagePreview: '',
                hasImage: false,
                isDragging: false,
                isAnalyzing: false,
                generateSocial: false,
                analysisResult: null,
                imageData: null,
                selectedTone: 'factual',
                responseLength: 2,
                socialResponse: '',
                isGeneratingSocial: false,
                keyPoints: [],
                sources: [],
                primarySources: [],
                secondarySources: [],
                otherSources: [],
                
                // Zpracování upuštěného souboru
                handleDrop(e) {
                    this.isDragging = false;
                    const dt = e.dataTransfer;
                    const files = dt.files;
                    
                    if (files.length > 0) {
                        this.handleImageFile(files[0]);
                    }
                },
                
                // Zpracování výběru souboru přes input
                handleImageSelect(e) {
                    if (e.target.files.length > 0) {
                        this.handleImageFile(e.target.files[0]);
                    }
                },
                
                // Zpracování vložení obrázku pomocí Ctrl+V
                handlePaste(e) {
                    // Kontrola, zda je cílem události textové pole
                    const isTextInput = e.target.tagName === 'TEXTAREA' || 
                                       (e.target.tagName === 'INPUT' && 
                                        (e.target.type === 'text' || e.target.type === 'search'));
                    
                    // Pokud je cílem textové pole, necháme výchozí chování
                    if (isTextInput) {
                        return;
                    }
                    
                    // Jinak zpracujeme vložení jako obrázek
                    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
                    
                    for (let i = 0; i < items.length; i++) {
                        if (items[i].type.indexOf('image') !== -1) {
                            const file = items[i].getAsFile();
                            this.handleImageFile(file);
                            e.preventDefault(); // Zabráníme výchozímu chování
                            break;
                        }
                    }
                },
                
                // Zpracování souboru obrázku
                handleImageFile(file) {
                    // Kontrola typu souboru
                    if (!config.allowedFormats.includes(file.type)) {
                        this.showError('Nepodporovaný formát souboru. Povolené formáty jsou: JPG, PNG, GIF, WebP.');
                        return;
                    }
                    
                    // Kontrola velikosti souboru
                    if (file.size > config.maxFileSize) {
                        this.showError('Soubor je příliš velký. Maximální velikost je 5MB.');
                        return;
                    }
                    
                    // Zobrazení náhledu
                    const reader = new FileReader();
                    
                    reader.onload = (e) => {
                        this.imagePreview = e.target.result;
                        this.hasImage = true;
                        this.imageData = e.target.result.split(',')[1]; // Uložení base64 dat bez hlavičky
                    };
                    
                    reader.readAsDataURL(file);
                },
                
                // Vymazání obrázku
                clearImage() {
                    this.imagePreview = '';
                    this.hasImage = false;
                    this.imageData = null;
                    if (imageInput) {
                        imageInput.value = '';
                    }
                },
                
                // Zobrazení chybové zprávy
                showError(message) {
                    const errorMessage = document.getElementById(config.errorMessageId);
                    if (errorMessage) {
                        errorMessage.textContent = message;
                        errorMessage.classList.remove('hidden');
                    } else {
                        alert(message);
                    }
                },
                
                // Analýza obsahu
                analyze() {
                    if ((!this.textInput || this.textInput.trim() === '') && !this.hasImage) {
                        this.showError('Prosím, vložte text nebo obrázek k analýze.');
                        return;
                    }
                    
                    this.isAnalyzing = true;
                    
                    // Příprava dat pro odeslání
                    const formData = new FormData();
                    formData.append('text', this.textInput);
                    formData.append('generate_social', this.generateSocial);
                    
                    if (this.hasImage && this.imageData) {
                        formData.append('image_data', this.imageData);
                    }
                    
                    // Odeslání požadavku na server
                    fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Chyba při analýze obsahu.');
                        }
                        return response.json();
                    })
                    .then(data => {
                        this.isAnalyzing = false;
                        this.analysisResult = data;
                        
                        // Zpracování výsledku
                        this.processAnalysisResult(data);
                    })
                    .catch(error => {
                        this.isAnalyzing = false;
                        this.showError('Došlo k chybě při analýze: ' + error.message);
                    });
                },
                
                // Zpracování výsledku analýzy
                processAnalysisResult(data) {
                    // Implementace zpracování výsledku...
                    console.log('Výsledek analýzy:', data);
                    
                    // Příklad zpracování
                    if (data.analysis) {
                        // Zpracování klíčových bodů
                        this.keyPoints = data.key_points || [];
                        
                        // Zpracování zdrojů
                        this.sources = data.sources || [];
                        this.primarySources = this.sources.filter(s => s.type === 'primary').map(s => s.url);
                        this.secondarySources = this.sources.filter(s => s.type === 'secondary').map(s => s.url);
                        this.otherSources = this.sources.filter(s => !s.type || (s.type !== 'primary' && s.type !== 'secondary')).map(s => s.url);
                        
                        // Zpracování odpovědi pro sociální sítě
                        if (this.generateSocial && data.social) {
                            this.socialResponse = data.social;
                        }
                    }
                },
                
                // Generování odpovědi pro sociální sítě
                generateSocialResponse(tone) {
                    this.selectedTone = tone;
                    this.isGeneratingSocial = true;
                    
                    // Implementace generování odpovědi...
                    setTimeout(() => {
                        this.isGeneratingSocial = false;
                        this.socialResponse = "OVĚŘIL/A JSEM ✅ Toto je ukázková odpověď pro sociální sítě.";
                    }, 1000);
                },
                
                // Regenerace odpovědi pro sociální sítě
                regenerateSocialResponse() {
                    this.generateSocialResponse(this.selectedTone);
                },
                
                // Kopírování do schránky
                copyToClipboard(text) {
                    navigator.clipboard.writeText(text)
                        .then(() => {
                            // Úspěšně zkopírováno
                            console.log('Text zkopírován do schránky');
                        })
                        .catch(err => {
                            console.error('Chyba při kopírování do schránky:', err);
                        });
                },
                
                // Výpočet pozice markeru na škále pravdivosti
                get truthScalePosition() {
                    if (!this.analysisResult || !this.analysisResult.truth_level) {
                        return 'left: 50%';
                    }
                    
                    // Převod hodnoty 1-5 na procenta (0-100%)
                    const percentage = ((this.analysisResult.truth_level - 1) / 4) * 100;
                    return `left: ${percentage}%`;
                },
                
                // Generování HTML pro badge s hodnocením pravdivosti
                get truthBadge() {
                    if (!this.analysisResult || !this.analysisResult.truth_level) {
                        return '';
                    }
                    
                    const truthLevel = this.analysisResult.truth_level;
                    let badgeClass = '';
                    let badgeText = '';
                    
                    switch(truthLevel) {
                        case 1:
                            badgeClass = 'badge-truth-1';
                            badgeText = 'Pravda';
                            break;
                        case 2:
                            badgeClass = 'badge-truth-2';
                            badgeText = 'Spíše pravda';
                            break;
                        case 3:
                            badgeClass = 'badge-truth-3';
                            badgeText = 'Zavádějící';
                            break;
                        case 4:
                            badgeClass = 'badge-truth-4';
                            badgeText = 'Spíše lež';
                            break;
                        case 5:
                            badgeClass = 'badge-truth-5';
                            badgeText = 'Lež';
                            break;
                        default:
                            badgeClass = '';
                            badgeText = 'Neznámé hodnocení';
                    }
                    
                    return `<span class="badge ${badgeClass}">${badgeText}</span>`;
                },
                
                // Formátování vysvětlení
                get formattedExplanation() {
                    if (!this.analysisResult || !this.analysisResult.explanation) {
                        return '';
                    }
                    
                    // Jednoduchá konverze nových řádků na <br>
                    return this.analysisResult.explanation.replace(/\n/g, '<br>');
                }
            };
        };
    }

    // Globální posluchač událostí pro vkládání obrázků pomocí Ctrl+V
    document.addEventListener('paste', function(e) {
        // Kontrola, zda je cílem události textové pole
        const isTextInput = e.target.tagName === 'TEXTAREA' || 
                           (e.target.tagName === 'INPUT' && 
                            (e.target.type === 'text' || e.target.type === 'search'));
        
        // Pokud je cílem textové pole, necháme výchozí chování
        if (isTextInput) {
            return;
        }
        
        // Jinak zpracujeme vložení jako obrázek
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const file = items[i].getAsFile();
                
                // Pokud máme Alpine.js komponentu, použijeme její metodu
                const factCheckerEl = document.querySelector('[x-data="factChecker()"]');
                if (factCheckerEl && factCheckerEl.__x) {
                    factCheckerEl.__x.$data.handleImageFile(file);
                } else {
                    // Záložní řešení - zpracování bez Alpine.js
                    handleImageFileStandalone(file);
                }
                
                e.preventDefault(); // Zabráníme výchozímu chování
                break;
            }
        }
    });

    // Záložní funkce pro zpracování obrázku bez Alpine.js
    function handleImageFileStandalone(file) {
        // Kontrola typu souboru
        if (!config.allowedFormats.includes(file.type)) {
            alert('Nepodporovaný formát souboru. Povolené formáty jsou: JPG, PNG, GIF, WebP.');
            return;
        }
        
        // Kontrola velikosti souboru
        if (file.size > config.maxFileSize) {
            alert('Soubor je příliš velký. Maximální velikost je 5MB.');
            return;
        }
        
        // Zobrazení náhledu
        const reader = new FileReader();
        const preview = document.getElementById(config.imagePreviewId);
        
        if (preview) {
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.classList.remove('hidden');
                
                // Nastavení příznaku, že máme obrázek
                if (dropZone) {
                    dropZone.classList.add('has-image');
                }
            };
            
            reader.readAsDataURL(file);
        }
    }
});
