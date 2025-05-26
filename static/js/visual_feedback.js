/**
 * Vylepšení vizuální zpětné vazby pro politweet-assistant
 * 
 * Tento soubor obsahuje JavaScript kód pro vylepšení vizuální zpětné vazby:
 * - Animace pro plynulejší přechody mezi stavy
 * - Interaktivní vizualizace hodnocení pravdivosti
 * - Rozbalovací/sbalovací sekce pro detailní informace
 * 
 * Jak implementovat:
 * 1. Přidejte tento soubor do adresáře static/js/
 * 2. Přidejte odkaz na tento soubor v base.html
 */

document.addEventListener('DOMContentLoaded', function() {
    // Konfigurace
    const config = {
        resultCardClass: 'result-card',
        collapsibleSectionClass: 'collapsible-section',
        collapsibleHeaderClass: 'collapsible-header',
        collapsibleContentClass: 'collapsible-content',
        truthMeterClass: 'truth-meter',
        truthLevelClass: 'truth-level',
        tooltipTriggerClass: 'tooltip-trigger',
        loadingClass: 'loading',
        fadeInClass: 'fade-in',
        slideInUpClass: 'slide-in-up'
    };

    // Inicializace animací pro výsledky analýzy
    initResultAnimations();
    
    // Inicializace rozbalovacích/sbalovacích sekcí
    initCollapsibleSections();
    
    // Inicializace vizualizace hodnocení pravdivosti
    initTruthMeter();
    
    // Inicializace tooltipů
    initTooltips();
    
    // Inicializace animací pro výsledky analýzy
    function initResultAnimations() {
        const resultCards = document.querySelectorAll(`.${config.resultCardClass}`);
        
        if (resultCards.length === 0) return;
        
        // Přidání tříd pro animace s postupným zpožděním
        resultCards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add(config.fadeInClass, config.slideInUpClass);
            }, index * 100);
        });
    }
    
    // Inicializace rozbalovacích/sbalovacích sekcí
    function initCollapsibleSections() {
        const collapsibleSections = document.querySelectorAll(`.${config.collapsibleSectionClass}`);
        
        if (collapsibleSections.length === 0) return;
        
        collapsibleSections.forEach(section => {
            const header = section.querySelector(`.${config.collapsibleHeaderClass}`);
            const content = section.querySelector(`.${config.collapsibleContentClass}`);
            
            if (!header || !content) return;
            
            // Přidání ikony pro rozbalení/sbalení
            const icon = document.createElement('span');
            icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/></svg>';
            icon.className = 'collapsible-icon';
            header.appendChild(icon);
            
            // Přidání události pro rozbalení/sbalení
            header.addEventListener('click', () => {
                section.classList.toggle('active');
            });
        });
    }
    
    // Inicializace vizualizace hodnocení pravdivosti
    function initTruthMeter() {
        const truthMeters = document.querySelectorAll(`.${config.truthMeterClass}`);
        
        if (truthMeters.length === 0) return;
        
        truthMeters.forEach(meter => {
            // Získání úrovně pravdivosti z atributu data-level
            const level = meter.getAttribute('data-level') || '3';
            
            // Vytvoření výplně pro vizualizaci
            const fill = document.createElement('div');
            fill.className = `truth-meter-fill truth-meter-fill-${level}`;
            meter.appendChild(fill);
            
            // Vytvoření popisků
            const labels = document.createElement('div');
            labels.className = 'truth-meter-labels';
            labels.innerHTML = `
                <span>Pravda</span>
                <span>Spíše pravda</span>
                <span>Zavádějící</span>
                <span>Spíše lež</span>
                <span>Lež</span>
            `;
            meter.insertAdjacentElement('afterend', labels);
            
            // Animace výplně
            setTimeout(() => {
                fill.style.width = `${level * 20}%`;
            }, 300);
        });
        
        // Přidání interaktivity pro štítky úrovně pravdivosti
        const truthLevels = document.querySelectorAll(`.${config.truthLevelClass}`);
        
        truthLevels.forEach(level => {
            level.addEventListener('mouseenter', () => {
                level.classList.add('pulse');
            });
            
            level.addEventListener('mouseleave', () => {
                level.classList.remove('pulse');
            });
        });
    }
    
    // Inicializace tooltipů
    function initTooltips() {
        const tooltipTriggers = document.querySelectorAll(`.${config.tooltipTriggerClass}`);
        
        if (tooltipTriggers.length === 0) return;
        
        tooltipTriggers.forEach(trigger => {
            // Získání obsahu tooltipu z atributu data-tooltip
            const tooltipContent = trigger.getAttribute('data-tooltip');
            
            if (!tooltipContent) return;
            
            // Vytvoření kontejneru pro tooltip
            const container = document.createElement('span');
            container.className = 'tooltip-container';
            
            // Přesunutí triggeru do kontejneru
            trigger.parentNode.insertBefore(container, trigger);
            container.appendChild(trigger);
            
            // Vytvoření obsahu tooltipu
            const tooltip = document.createElement('span');
            tooltip.className = 'tooltip-content';
            tooltip.textContent = tooltipContent;
            container.appendChild(tooltip);
        });
    }
    
    // Funkce pro zobrazení stavu načítání
    window.showLoading = function(element, message = 'Načítání...') {
        if (!element) return;
        
        // Uložení původního obsahu
        element.setAttribute('data-original-content', element.innerHTML);
        
        // Zobrazení stavu načítání
        element.classList.add(config.loadingClass);
        
        // Vytvoření spinneru
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        // Vytvoření zprávy
        const messageElement = document.createElement('span');
        messageElement.textContent = message;
        messageElement.style.marginLeft = '0.5rem';
        
        // Vymazání původního obsahu a přidání spinneru a zprávy
        element.innerHTML = '';
        element.appendChild(spinner);
        element.appendChild(messageElement);
        
        return {
            // Funkce pro ukončení stavu načítání
            done: function(newContent = null) {
                element.classList.remove(config.loadingClass);
                
                if (newContent) {
                    // Nastavení nového obsahu
                    element.innerHTML = newContent;
                } else {
                    // Obnovení původního obsahu
                    element.innerHTML = element.getAttribute('data-original-content');
                }
                
                // Přidání animace pro plynulý přechod
                element.classList.add(config.fadeInClass);
                
                // Odstranění animace po dokončení
                setTimeout(() => {
                    element.classList.remove(config.fadeInClass);
                }, 300);
            }
        };
    };
    
    // Funkce pro zobrazení výsledku analýzy s animací
    window.showAnalysisResult = function(container, resultHTML) {
        if (!container) return;
        
        // Vymazání původního obsahu
        container.innerHTML = '';
        
        // Přidání nového obsahu
        container.innerHTML = resultHTML;
        
        // Inicializace všech komponent v novém obsahu
        initResultAnimations();
        initCollapsibleSections();
        initTruthMeter();
        initTooltips();
    };
    
    // Funkce pro zvýraznění klíčových částí textu
    window.highlightText = function(element, keywords, className = 'highlight') {
        if (!element || !keywords || !keywords.length) return;
        
        const text = element.innerHTML;
        let highlightedText = text;
        
        keywords.forEach(keyword => {
            const regex = new RegExp(`(${keyword})`, 'gi');
            highlightedText = highlightedText.replace(regex, `<span class="${className}">$1</span>`);
        });
        
        element.innerHTML = highlightedText;
    };
    
    // Funkce pro vytvoření animovaného přechodu mezi stránkami
    window.pageTransition = function(callback) {
        // Vytvoření překrytí pro animaci
        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = '#ffffff';
        overlay.style.zIndex = '9999';
        overlay.style.opacity = '0';
        overlay.style.transition = 'opacity 0.3s ease';
        
        document.body.appendChild(overlay);
        
        // Animace překrytí
        setTimeout(() => {
            overlay.style.opacity = '1';
            
            setTimeout(() => {
                // Provedení callbacku
                if (typeof callback === 'function') {
                    callback();
                }
                
                // Animace zmizení překrytí
                setTimeout(() => {
                    overlay.style.opacity = '0';
                    
                    // Odstranění překrytí po dokončení animace
                    setTimeout(() => {
                        document.body.removeChild(overlay);
                    }, 300);
                }, 50);
            }, 300);
        }, 0);
    };
});

/**
 * Poznámka: Pro plnou funkčnost tohoto kódu je potřeba přidat následující HTML elementy:
 * 
 * <!-- Vizualizace hodnocení pravdivosti -->
 * <div class="truth-meter" data-level="3"></div>
 * 
 * <!-- Štítek úrovně pravdivosti -->
 * <span class="truth-level truth-level-3">Zavádějící</span>
 * 
 * <!-- Rozbalovací sekce -->
 * <div class="collapsible-section">
 *   <div class="collapsible-header">
 *     <h3>Detailní vysvětlení</h3>
 *   </div>
 *   <div class="collapsible-content">
 *     <p>Obsah rozbalovací sekce...</p>
 *   </div>
 * </div>
 * 
 * <!-- Tooltip -->
 * <span class="tooltip-trigger" data-tooltip="Vysvětlení pojmu">Pojem</span>
 * 
 * Také je potřeba přidat odpovídající CSS styly z visual_feedback.css.
 */
