/**
 * Hlavní JavaScript soubor pro Fact-Checking aplikaci
 * Obsahuje funkce pro interaktivní prvky, vizualizace a zpracování výsledků
 */

// Globální proměnné
let currentAnalysisResult = null;
let chartInstances = {};

// Inicializace po načtení dokumentu
document.addEventListener('DOMContentLoaded', function() {
    // Inicializace formuláře
    initForm();
    
    // Inicializace interaktivních prvků
    initInteractiveElements();
    
    // Nastavení přepínačů zobrazení
    initDisplayToggles();
    
    // Nastavení exportních funkcí
    initExportFunctions();
});

/**
 * Inicializace formuláře pro fact-checking
 */
function initForm() {
    const form = document.getElementById('fact-check-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Zobrazení indikátoru načítání
        showLoadingIndicator();
        
        // Získání hodnot z formuláře
        const formData = new FormData(form);
        
        // Odeslání požadavku na server
        fetch('/api/check-facts', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Uložení výsledku
            currentAnalysisResult = data;
            
            // Zobrazení výsledků
            displayResults(data);
            
            // Skrytí indikátoru načítání
            hideLoadingIndicator();
            
            // Přesměrování na stránku s výsledky (pokud je to potřeba)
            if (window.location.pathname !== '/results') {
                window.location.href = '/results';
            }
        })
        .catch(error => {
            console.error('Chyba při zpracování požadavku:', error);
            showErrorMessage('Došlo k chybě při zpracování požadavku. Zkuste to prosím znovu.');
            hideLoadingIndicator();
        });
    });
    
    // Inicializace nastavení expertízy a délky analýzy
    initExpertiseLevelSlider();
    initAnalysisLengthSlider();
    
    // Inicializace přepínačů typu obsahu
    initContentTypeToggles();
}

/**
 * Inicializace posuvníku pro úroveň expertízy
 */
function initExpertiseLevelSlider() {
    const slider = document.getElementById('expertise-level-slider');
    const valueDisplay = document.getElementById('expertise-level-value');
    const descriptions = {
        'basic': 'Základní analýza pro běžné uživatele',
        'medium': 'Středně pokročilá analýza s více detaily',
        'advanced': 'Pokročilá analýza s odbornými termíny',
        'expert': 'Expertní analýza s maximální hloubkou'
    };
    
    if (!slider || !valueDisplay) return;
    
    // Nastavení výchozí hodnoty
    updateExpertiseLevel(slider.value);
    
    // Aktualizace při změně hodnoty
    slider.addEventListener('input', function() {
        updateExpertiseLevel(this.value);
    });
    
    function updateExpertiseLevel(value) {
        let level;
        if (value <= 25) {
            level = 'basic';
        } else if (value <= 50) {
            level = 'medium';
        } else if (value <= 75) {
            level = 'advanced';
        } else {
            level = 'expert';
        }
        
        // Aktualizace zobrazené hodnoty
        valueDisplay.textContent = level.charAt(0).toUpperCase() + level.slice(1);
        
        // Aktualizace skrytého pole
        document.getElementById('expertise_level').value = level;
        
        // Aktualizace popisu
        const descriptionElement = document.getElementById('expertise-level-description');
        if (descriptionElement) {
            descriptionElement.textContent = descriptions[level];
        }
    }
}

/**
 * Inicializace posuvníku pro délku analýzy
 */
function initAnalysisLengthSlider() {
    const slider = document.getElementById('analysis-length-slider');
    const valueDisplay = document.getElementById('analysis-length-value');
    const descriptions = {
        'brief': 'Stručná analýza s klíčovými body',
        'standard': 'Standardní analýza s vyváženým detailem',
        'detailed': 'Detailní analýza s hlubším rozborem',
        'exhaustive': 'Vyčerpávající analýza s maximem detailů'
    };
    
    if (!slider || !valueDisplay) return;
    
    // Nastavení výchozí hodnoty
    updateAnalysisLength(slider.value);
    
    // Aktualizace při změně hodnoty
    slider.addEventListener('input', function() {
        updateAnalysisLength(this.value);
    });
    
    function updateAnalysisLength(value) {
        let length;
        if (value <= 25) {
            length = 'brief';
        } else if (value <= 50) {
            length = 'standard';
        } else if (value <= 75) {
            length = 'detailed';
        } else {
            length = 'exhaustive';
        }
        
        // Aktualizace zobrazené hodnoty
        valueDisplay.textContent = length.charAt(0).toUpperCase() + length.slice(1);
        
        // Aktualizace skrytého pole
        document.getElementById('analysis_length').value = length;
        
        // Aktualizace popisu
        const descriptionElement = document.getElementById('analysis-length-description');
        if (descriptionElement) {
            descriptionElement.textContent = descriptions[length];
        }
    }
}

/**
 * Inicializace přepínačů typu obsahu
 */
function initContentTypeToggles() {
    const contentTypeRadios = document.querySelectorAll('input[name="content_type"]');
    const contentInputs = {
        'text': document.getElementById('text-input-container'),
        'image': document.getElementById('image-input-container'),
        'audio': document.getElementById('audio-input-container'),
        'video': document.getElementById('video-input-container')
    };
    
    if (!contentTypeRadios.length) return;
    
    // Skrytí všech vstupů kromě výchozího
    for (const type in contentInputs) {
        if (contentInputs[type]) {
            contentInputs[type].style.display = 'none';
        }
    }
    
    // Zobrazení výchozího vstupu
    if (contentInputs['text']) {
        contentInputs['text'].style.display = 'block';
    }
    
    // Přepínání vstupů podle vybraného typu
    contentTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            for (const type in contentInputs) {
                if (contentInputs[type]) {
                    contentInputs[type].style.display = 'none';
                }
            }
            
            const selectedType = this.value;
            if (contentInputs[selectedType]) {
                contentInputs[selectedType].style.display = 'block';
            }
        });
    });
}

/**
 * Inicializace interaktivních prvků
 */
function initInteractiveElements() {
    // Inicializace tooltipů
    initTooltips();
    
    // Inicializace rozbalovacích sekcí
    initCollapsibleSections();
    
    // Inicializace záložek
    initTabs();
}

/**
 * Inicializace tooltipů
 */
function initTooltips() {
    const tooltips = document.querySelectorAll('.tooltip-trigger');
    
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipContent = this.querySelector('.tooltip-content');
            if (tooltipContent) {
                tooltipContent.style.display = 'block';
            }
        });
        
        tooltip.addEventListener('mouseleave', function() {
            const tooltipContent = this.querySelector('.tooltip-content');
            if (tooltipContent) {
                tooltipContent.style.display = 'none';
            }
        });
    });
}

/**
 * Inicializace rozbalovacích sekcí
 */
function initCollapsibleSections() {
    const collapsibleHeaders = document.querySelectorAll('.collapsible-header');
    
    collapsibleHeaders.forEach(header => {
        header.addEventListener('click', function() {
            this.classList.toggle('active');
            
            const content = this.nextElementSibling;
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    });
}

/**
 * Inicializace záložek
 */
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Deaktivace všech záložek
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Aktivace vybrané záložky
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

/**
 * Inicializace přepínačů zobrazení
 */
function initDisplayToggles() {
    const viewToggles = document.querySelectorAll('.view-toggle');
    
    viewToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const viewType = this.getAttribute('data-view');
            
            // Deaktivace všech přepínačů
            document.querySelectorAll('.view-toggle').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Aktivace vybraného přepínače
            this.classList.add('active');
            
            // Přepnutí zobrazení
            switchView(viewType);
        });
    });
}

/**
 * Přepnutí zobrazení výsledků
 */
function switchView(viewType) {
    const viewContainers = document.querySelectorAll('.view-container');
    
    viewContainers.forEach(container => {
        container.style.display = 'none';
    });
    
    const selectedView = document.getElementById(viewType + '-view');
    if (selectedView) {
        selectedView.style.display = 'block';
    }
    
    // Aktualizace grafů při přepnutí zobrazení
    if (viewType === 'visual' && currentAnalysisResult) {
        setTimeout(() => {
            renderCharts(currentAnalysisResult);
        }, 100);
    }
}

/**
 * Inicializace exportních funkcí
 */
function initExportFunctions() {
    const exportButtons = {
        'pdf': document.getElementById('export-pdf'),
        'image': document.getElementById('export-image'),
        'json': document.getElementById('export-json'),
        'text': document.getElementById('export-text')
    };
    
    // Export do PDF
    if (exportButtons.pdf) {
        exportButtons.pdf.addEventListener('click', function() {
            exportToPDF();
        });
    }
    
    // Export do obrázku
    if (exportButtons.image) {
        exportButtons.image.addEventListener('click', function() {
            exportToImage();
        });
    }
    
    // Export do JSON
    if (exportButtons.json) {
        exportButtons.json.addEventListener('click', function() {
            exportToJSON();
        });
    }
    
    // Export do textového souboru
    if (exportButtons.text) {
        exportButtons.text.addEventListener('click', function() {
            exportToText();
        });
    }
}

/**
 * Zobrazení výsledků fact-checkingu
 */
function displayResults(data) {
    if (!data) return;
    
    // Zobrazení základních informací
    displayBasicInfo(data);
    
    // Zobrazení hodnocení pravdivosti
    displayTruthRating(data);
    
    // Zobrazení klíčových bodů
    displayKeyPoints(data);
    
    // Zobrazení detailního vysvětlení
    displayDetailedExplanation(data);
    
    // Zobrazení ověřených tvrzení
    displayVerifiedClaims(data);
    
    // Zobrazení hodnocení zdrojů
    displaySourceEvaluation(data);
    
    // Zobrazení alternativních perspektiv
    displayAlternativePerspectives(data);
    
    // Zobrazení navrhovaných reakcí
    displaySuggestedResponses(data);
    
    // Vykreslení grafů a vizualizací
    renderCharts(data);
}

/**
 * Zobrazení základních informací
 */
function displayBasicInfo(data) {
    const elements = {
        'content-type': document.getElementById('result-content-type'),
        'content-summary': document.getElementById('result-content-summary'),
        'timestamp': document.getElementById('result-timestamp'),
        'expertise-level': document.getElementById('result-expertise-level'),
        'analysis-length': document.getElementById('result-analysis-length')
    };
    
    if (elements['content-type']) {
        elements['content-type'].textContent = getContentTypeLabel(data.content_type);
    }
    
    if (elements['content-summary']) {
        elements['content-summary'].textContent = data.content_summary;
    }
    
    if (elements['timestamp']) {
        elements['timestamp'].textContent = formatDateTime(data.timestamp);
    }
    
    if (elements['expertise-level']) {
        elements['expertise-level'].textContent = getExpertiseLevelLabel(data.settings.expertise_level);
    }
    
    if (elements['analysis-length']) {
        elements['analysis-length'].textContent = getAnalysisLengthLabel(data.settings.analysis_length);
    }
}

/**
 * Zobrazení hodnocení pravdivosti
 */
function displayTruthRating(data) {
    const elements = {
        'truth-rating': document.getElementById('truth-rating'),
        'truth-score': document.getElementById('truth-score'),
        'truth-description': document.getElementById('truth-description'),
        'truth-meter': document.getElementById('truth-meter'),
        'truth-meter-value': document.getElementById('truth-meter-value'),
        'truth-meter-label': document.getElementById('truth-meter-label')
    };
    
    if (elements['truth-rating']) {
        elements['truth-rating'].textContent = data.truth_rating;
        elements['truth-rating'].style.color = data.truth_color;
    }
    
    if (elements['truth-score']) {
        elements['truth-score'].textContent = (data.truth_score * 100).toFixed(0) + '%';
    }
    
    if (elements['truth-description']) {
        elements['truth-description'].textContent = data.truth_description;
    }
    
    // Aktualizace měřidla pravdivosti
    if (elements['truth-meter-value']) {
        elements['truth-meter-value'].style.width = (data.truth_score * 100) + '%';
        elements['truth-meter-value'].style.backgroundColor = data.truth_color;
    }
    
    if (elements['truth-meter-label']) {
        elements['truth-meter-label'].textContent = data.truth_rating;
        elements['truth-meter-label'].style.color = data.truth_color;
    }
}

/**
 * Zobrazení klíčových bodů
 */
function displayKeyPoints(data) {
    const keyPointsList = document.getElementById('key-points-list');
    if (!keyPointsList || !data.analysis.key_points) return;
    
    // Vyčištění seznamu
    keyPointsList.innerHTML = '';
    
    // Přidání klíčových bodů
    data.analysis.key_points.forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        keyPointsList.appendChild(li);
    });
}

/**
 * Zobrazení detailního vysvětlení
 */
function displayDetailedExplanation(data) {
    const explanationElement = document.getElementById('detailed-explanation');
    if (!explanationElement || !data.analysis.detailed_explanation) return;
    
    explanationElement.innerHTML = data.analysis.detailed_explanation.replace(/\n/g, '<br>');
}

/**
 * Zobrazení ověřených tvrzení
 */
function displayVerifiedClaims(data) {
    const claimsContainer = document.getElementById('verified-claims-container');
    if (!claimsContainer || !data.analysis.claims) return;
    
    // Vyčištění kontejneru
    claimsContainer.innerHTML = '';
    
    // Přidání ověřených tvrzení
    data.analysis.claims.forEach((claim, index) => {
        const claimElement = document.createElement('div');
        claimElement.className = 'claim-card';
        claimElement.style.borderLeft = `4px solid ${claim.color}`;
        
        const claimContent = `
            <div class="claim-header">
                <span class="claim-number">#${index + 1}</span>
                <span class="claim-rating" style="color: ${claim.color}">${claim.rating}</span>
            </div>
            <div class="claim-text">${claim.text}</div>
            <div class="claim-explanation">${claim.explanation}</div>
            <div class="claim-sources">
                <strong>Zdroje:</strong>
                <ul>
                    ${claim.sources.map(source => `
                        <li><a href="${source.url}" target="_blank">${source.name}</a></li>
                    `).join('')}
                </ul>
            </div>
        `;
        
        claimElement.innerHTML = claimContent;
        claimsContainer.appendChild(claimElement);
    });
}

/**
 * Zobrazení hodnocení zdrojů
 */
function displaySourceEvaluation(data) {
    const sourcesContainer = document.getElementById('sources-container');
    if (!sourcesContainer || !data.analysis.sources) return;
    
    // Vyčištění kontejneru
    sourcesContainer.innerHTML = '';
    
    // Přidání hodnocení zdrojů
    data.analysis.sources.forEach(source => {
        const sourceElement = document.createElement('div');
        sourceElement.className = 'source-card';
        
        // Výpočet barvy pro spolehlivost
        const reliabilityColor = getReliabilityColor(source.reliability_score);
        
        const sourceContent = `
            <div class="source-header">
                <h3 class="source-name">${source.source_info.name}</h3>
                <span class="source-reliability" style="color: ${reliabilityColor}">
                    ${source.reliability_level}
                </span>
            </div>
            <div class="source-url">
                <a href="${source.url}" target="_blank">${source.domain}</a>
            </div>
            <div class="source-factors">
                <h4>Faktory hodnocení:</h4>
                <ul>
                    ${Object.entries(source.evaluation_factors).map(([factor, data]) => `
                        <li>
                            <strong>${getFactorLabel(factor)}:</strong>
                            <div class="factor-bar-container">
                                <div class="factor-bar" style="width: ${data.score * 100}%"></div>
                            </div>
                            <span class="factor-score">${(data.score * 100).toFixed(0)}%</span>
                            <p class="factor-description">${data.description}</p>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
        
        sourceElement.innerHTML = sourceContent;
        sourcesContainer.appendChild(sourceElement);
    });
}

/**
 * Zobrazení alternativních perspektiv
 */
function displayAlternativePerspectives(data) {
    const perspectivesContainer = document.getElementById('perspectives-container');
    if (!perspectivesContainer || !data.analysis.alternative_perspectives) return;
    
    // Vyčištění kontejneru
    perspectivesContainer.innerHTML = '';
    
    // Přidání alternativních perspektiv
    data.analysis.alternative_perspectives.forEach(perspective => {
        const perspectiveElement = document.createElement('div');
        perspectiveElement.className = 'perspective-card';
        
        const perspectiveContent = `
            <h3 class="perspective-title">${perspective.title}</h3>
            <div class="perspective-description">${perspective.description}</div>
        `;
        
        perspectiveElement.innerHTML = perspectiveContent;
        perspectivesContainer.appendChild(perspectiveElement);
    });
}

/**
 * Zobrazení navrhovaných reakcí
 */
function displaySuggestedResponses(data) {
    const responsesContainer = document.getElementById('responses-container');
    if (!responsesContainer || !data.analysis.suggested_responses) return;
    
    // Vyčištění kontejneru
    responsesContainer.innerHTML = '';
    
    // Přidání navrhovaných reakcí
    data.analysis.suggested_responses.forEach(response => {
        const responseElement = document.createElement('div');
        responseElement.className = 'response-card';
        responseElement.dataset.type = response.type;
        
        const responseContent = `
            <div class="response-icon">
                <i class="material-icons">${response.icon}</i>
            </div>
            <div class="response-text">${response.text}</div>
            <div class="response-actions">
                <button class="copy-btn" onclick="copyToClipboard('${response.text.replace(/'/g, "\\'")}')">
                    <i class="material-icons">content_copy</i> Kopírovat
                </button>
                <button class="share-btn" onclick="shareResponse('${response.text.replace(/'/g, "\\'")}')">
                    <i class="material-icons">share</i> Sdílet
                </button>
            </div>
        `;
        
        responseElement.innerHTML = responseContent;
        responsesContainer.appendChild(responseElement);
    });
}

/**
 * Vykreslení grafů a vizualizací
 */
function renderCharts(data) {
    // Vykreslení grafu hodnocení pravdivosti
    renderTruthRatingChart(data);
    
    // Vykreslení grafu distribuce hodnocení tvrzení
    renderClaimsDistributionChart(data);
    
    // Vykreslení grafu hodnocení zdrojů
    renderSourcesChart(data);
}

/**
 * Vykreslení grafu hodnocení pravdivosti
 */
function renderTruthRatingChart(data) {
    const chartCanvas = document.getElementById('truth-rating-chart');
    if (!chartCanvas) return;
    
    // Zničení existujícího grafu
    if (chartInstances.truthRating) {
        chartInstances.truthRating.destroy();
    }
    
    // Vytvoření nového grafu
    const ctx = chartCanvas.getContext('2d');
    chartInstances.truthRating = new Chart(ctx, {
        type: 'gauge',
        data: {
            datasets: [{
                value: data.truth_score,
                data: [0.2, 0.4, 0.6, 0.8, 1.0],
                backgroundColor: ['#EA4335', '#F57C00', '#FBBC05', '#4CAF50', '#34A853'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Hodnocení pravdivosti'
            },
            layout: {
                padding: {
                    bottom: 30
                }
            },
            needle: {
                radiusPercentage: 2,
                widthPercentage: 3.2,
                lengthPercentage: 80,
                color: 'rgba(0, 0, 0, 1)'
            },
            valueLabel: {
                display: true,
                formatter: function(value) {
                    return data.truth_rating;
                },
                color: data.truth_color,
                fontSize: 20,
                borderColor: 'rgba(0, 0, 0, 0.1)',
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                borderRadius: 5,
                padding: {
                    top: 10,
                    bottom: 10
                }
            }
        }
    });
}

/**
 * Vykreslení grafu distribuce hodnocení tvrzení
 */
function renderClaimsDistributionChart(data) {
    const chartCanvas = document.getElementById('claims-distribution-chart');
    if (!chartCanvas || !data.analysis.claims) return;
    
    // Zničení existujícího grafu
    if (chartInstances.claimsDistribution) {
        chartInstances.claimsDistribution.destroy();
    }
    
    // Příprava dat pro graf
    const ratingCounts = {};
    const ratingColors = {};
    
    data.analysis.claims.forEach(claim => {
        ratingCounts[claim.rating] = (ratingCounts[claim.rating] || 0) + 1;
        ratingColors[claim.rating] = claim.color;
    });
    
    const labels = Object.keys(ratingCounts);
    const values = Object.values(ratingCounts);
    const colors = labels.map(label => ratingColors[label]);
    
    // Vytvoření nového grafu
    const ctx = chartCanvas.getContext('2d');
    chartInstances.claimsDistribution = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: 'white',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Distribuce hodnocení tvrzení'
            },
            legend: {
                position: 'right'
            }
        }
    });
}

/**
 * Vykreslení grafu hodnocení zdrojů
 */
function renderSourcesChart(data) {
    const chartCanvas = document.getElementById('sources-chart');
    if (!chartCanvas || !data.analysis.sources) return;
    
    // Zničení existujícího grafu
    if (chartInstances.sources) {
        chartInstances.sources.destroy();
    }
    
    // Příprava dat pro graf
    const sourceNames = data.analysis.sources.map(source => source.source_info.name);
    const reliabilityScores = data.analysis.sources.map(source => source.reliability_score);
    const reliabilityColors = data.analysis.sources.map(source => getReliabilityColor(source.reliability_score));
    
    // Vytvoření nového grafu
    const ctx = chartCanvas.getContext('2d');
    chartInstances.sources = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sourceNames,
            datasets: [{
                label: 'Důvěryhodnost zdrojů',
                data: reliabilityScores,
                backgroundColor: reliabilityColors,
                borderColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Hodnocení důvěryhodnosti zdrojů'
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        max: 1,
                        callback: function(value) {
                            return (value * 100) + '%';
                        }
                    }
                }]
            }
        }
    });
}

/**
 * Export výsledků do PDF
 */
function exportToPDF() {
    if (!currentAnalysisResult) {
        showErrorMessage('Nejsou k dispozici žádné výsledky k exportu.');
        return;
    }
    
    showLoadingIndicator();
    
    // Odeslání požadavku na server pro generování PDF
    fetch('/api/export/pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            result_id: currentAnalysisResult.id
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Chyba při generování PDF');
        }
        return response.blob();
    })
    .then(blob => {
        // Vytvoření URL pro stažení
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `fact-check-${currentAnalysisResult.id}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        hideLoadingIndicator();
    })
    .catch(error => {
        console.error('Chyba při exportu do PDF:', error);
        showErrorMessage('Došlo k chybě při exportu do PDF. Zkuste to prosím znovu.');
        hideLoadingIndicator();
    });
}

/**
 * Export výsledků do obrázku
 */
function exportToImage() {
    if (!currentAnalysisResult) {
        showErrorMessage('Nejsou k dispozici žádné výsledky k exportu.');
        return;
    }
    
    showLoadingIndicator();
    
    // Použití html2canvas pro vytvoření obrázku
    const resultsContainer = document.getElementById('results-container');
    
    html2canvas(resultsContainer, {
        scale: 2,
        logging: false,
        useCORS: true
    }).then(canvas => {
        // Vytvoření URL pro stažení
        const url = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `fact-check-${currentAnalysisResult.id}.png`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        hideLoadingIndicator();
    }).catch(error => {
        console.error('Chyba při exportu do obrázku:', error);
        showErrorMessage('Došlo k chybě při exportu do obrázku. Zkuste to prosím znovu.');
        hideLoadingIndicator();
    });
}

/**
 * Export výsledků do JSON
 */
function exportToJSON() {
    if (!currentAnalysisResult) {
        showErrorMessage('Nejsou k dispozici žádné výsledky k exportu.');
        return;
    }
    
    // Vytvoření URL pro stažení
    const jsonString = JSON.stringify(currentAnalysisResult, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `fact-check-${currentAnalysisResult.id}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Export výsledků do textového souboru
 */
function exportToText() {
    if (!currentAnalysisResult) {
        showErrorMessage('Nejsou k dispozici žádné výsledky k exportu.');
        return;
    }
    
    // Vytvoření textového obsahu
    let textContent = `VÝSLEDKY FACT-CHECKINGU\n`;
    textContent += `======================\n\n`;
    textContent += `Datum a čas: ${formatDateTime(currentAnalysisResult.timestamp)}\n`;
    textContent += `Typ obsahu: ${getContentTypeLabel(currentAnalysisResult.content_type)}\n`;
    textContent += `Hodnocení pravdivosti: ${currentAnalysisResult.truth_rating} (${(currentAnalysisResult.truth_score * 100).toFixed(0)}%)\n\n`;
    textContent += `${currentAnalysisResult.truth_description}\n\n`;
    textContent += `DETAILNÍ VYSVĚTLENÍ\n`;
    textContent += `------------------\n`;
    textContent += `${currentAnalysisResult.analysis.detailed_explanation}\n\n`;
    textContent += `KLÍČOVÉ BODY\n`;
    textContent += `-----------\n`;
    currentAnalysisResult.analysis.key_points.forEach((point, index) => {
        textContent += `${index + 1}. ${point}\n`;
    });
    textContent += `\n`;
    textContent += `OVĚŘENÁ TVRZENÍ\n`;
    textContent += `---------------\n`;
    currentAnalysisResult.analysis.claims.forEach((claim, index) => {
        textContent += `Tvrzení #${index + 1}: ${claim.text}\n`;
        textContent += `Hodnocení: ${claim.rating}\n`;
        textContent += `Vysvětlení: ${claim.explanation}\n`;
        textContent += `Zdroje:\n`;
        claim.sources.forEach(source => {
            textContent += `- ${source.name} (${source.url})\n`;
        });
        textContent += `\n`;
    });
    textContent += `HODNOCENÍ ZDROJŮ\n`;
    textContent += `---------------\n`;
    currentAnalysisResult.analysis.sources.forEach((source, index) => {
        textContent += `Zdroj #${index + 1}: ${source.source_info.name} (${source.url})\n`;
        textContent += `Důvěryhodnost: ${source.reliability_level} (${(source.reliability_score * 100).toFixed(0)}%)\n`;
        textContent += `\n`;
    });
    
    // Vytvoření URL pro stažení
    const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `fact-check-${currentAnalysisResult.id}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Kopírování textu do schránky
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showSuccessMessage('Text byl zkopírován do schránky.');
    }).catch(err => {
        console.error('Chyba při kopírování do schránky:', err);
        showErrorMessage('Nepodařilo se zkopírovat text do schránky.');
    });
}

/**
 * Sdílení reakce
 */
function shareResponse(text) {
    if (navigator.share) {
        navigator.share({
            title: 'Fact-Check výsledek',
            text: text
        }).then(() => {
            console.log('Úspěšně sdíleno');
        }).catch(err => {
            console.error('Chyba při sdílení:', err);
            showErrorMessage('Nepodařilo se sdílet obsah.');
        });
    } else {
        copyToClipboard(text);
    }
}

/**
 * Zobrazení indikátoru načítání
 */
function showLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'flex';
    }
}

/**
 * Skrytí indikátoru načítání
 */
function hideLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}

/**
 * Zobrazení chybové zprávy
 */
function showErrorMessage(message) {
    const errorToast = document.getElementById('error-toast');
    const errorMessage = document.getElementById('error-message');
    
    if (errorToast && errorMessage) {
        errorMessage.textContent = message;
        errorToast.classList.add('show');
        
        setTimeout(() => {
            errorToast.classList.remove('show');
        }, 5000);
    } else {
        alert(message);
    }
}

/**
 * Zobrazení úspěšné zprávy
 */
function showSuccessMessage(message) {
    const successToast = document.getElementById('success-toast');
    const successMessage = document.getElementById('success-message');
    
    if (successToast && successMessage) {
        successMessage.textContent = message;
        successToast.classList.add('show');
        
        setTimeout(() => {
            successToast.classList.remove('show');
        }, 3000);
    }
}

/**
 * Formátování data a času
 */
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('cs-CZ');
}

/**
 * Získání popisku typu obsahu
 */
function getContentTypeLabel(contentType) {
    const labels = {
        'text': 'Text',
        'image': 'Obrázek',
        'audio': 'Audio',
        'video': 'Video'
    };
    
    return labels[contentType] || contentType;
}

/**
 * Získání popisku úrovně expertízy
 */
function getExpertiseLevelLabel(level) {
    const labels = {
        'basic': 'Základní',
        'medium': 'Střední',
        'advanced': 'Pokročilá',
        'expert': 'Expertní'
    };
    
    return labels[level] || level;
}

/**
 * Získání popisku délky analýzy
 */
function getAnalysisLengthLabel(length) {
    const labels = {
        'brief': 'Stručná',
        'standard': 'Standardní',
        'detailed': 'Detailní',
        'exhaustive': 'Vyčerpávající'
    };
    
    return labels[length] || length;
}

/**
 * Získání popisku faktoru hodnocení
 */
function getFactorLabel(factor) {
    const labels = {
        'expertise': 'Odbornost',
        'transparency': 'Transparentnost',
        'past_accuracy': 'Přesnost v minulosti',
        'editorial_process': 'Redakční proces',
        'independence': 'Nezávislost',
        'recency': 'Aktuálnost',
        'citation_quality': 'Kvalita citací'
    };
    
    return labels[factor] || factor;
}

/**
 * Získání barvy pro spolehlivost
 */
function getReliabilityColor(score) {
    if (score >= 0.9) {
        return '#34A853';  // zelená
    } else if (score >= 0.75) {
        return '#4CAF50';  // světlejší zelená
    } else if (score >= 0.6) {
        return '#FBBC05';  // žlutá
    } else if (score >= 0.4) {
        return '#F57C00';  // oranžová
    } else if (score >= 0.2) {
        return '#EA4335';  // červená
    } else {
        return '#B71C1C';  // tmavě červená
    }
}
