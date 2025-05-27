/**
 * Vylepšení pro mobilní dotykové ovládání pro politweet-assistant
 * 
 * Tento soubor obsahuje JavaScript kód pro lepší podporu dotykových zařízení:
 * - Vylepšené ovládání pro dotykové obrazovky
 * - Detekce dotykových gest
 * - Optimalizace pro mobilní prohlížeče
 * 
 * Jak implementovat:
 * 1. Přidejte tento soubor do adresáře static/js/
 * 2. Přidejte odkaz na tento soubor v base.html
 */

document.addEventListener('DOMContentLoaded', function() {
    // Detekce dotykového zařízení
    const isTouchDevice = ('ontouchstart' in window) || 
                          (navigator.maxTouchPoints > 0) || 
                          (navigator.msMaxTouchPoints > 0);
    
    // Přidání třídy k body elementu pro CSS optimalizace
    if (isTouchDevice) {
        document.body.classList.add('touch-device');
    }
    
    // Konfigurace
    const config = {
        dropZoneId: 'dropZone',
        imagePreviewId: 'imagePreview',
        textInputId: 'textInput',
        submitButtonId: 'submitButton',
        navToggleId: 'navToggle',
        navMenuId: 'navMenu',
        tapDelay: 300, // ms
        doubleTapDelay: 300, // ms
        longPressDelay: 500, // ms
        swipeThreshold: 50 // px
    };
    
    // Získání referencí na DOM elementy
    const dropZone = document.getElementById(config.dropZoneId);
    const imagePreview = document.getElementById(config.imagePreviewId);
    const textInput = document.getElementById(config.textInputId);
    const submitButton = document.getElementById(config.submitButtonId);
    const navToggle = document.getElementById(config.navToggleId);
    const navMenu = document.getElementById(config.navMenuId);
    
    // Proměnné pro sledování dotyků
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    let lastTapTime = 0;
    let longPressTimer = null;
    
    // Vylepšení pro drop zónu na dotykových zařízeních
    if (dropZone && isTouchDevice) {
        // Zabránění výchozímu chování prohlížeče pro dotyková gesta
        dropZone.addEventListener('touchstart', function(e) {
            // Uložení počáteční pozice dotyku
            touchStartX = e.changedTouches[0].screenX;
            touchStartY = e.changedTouches[0].screenY;
            
            // Přidání vizuální zpětné vazby
            this.classList.add('touch-active');
            
            // Nastavení časovače pro dlouhý stisk
            longPressTimer = setTimeout(() => {
                // Akce pro dlouhý stisk - např. zobrazení nápovědy
                showTouchHelp(this);
            }, config.longPressDelay);
        }, { passive: false });
        
        dropZone.addEventListener('touchend', function(e) {
            // Uložení koncové pozice dotyku
            touchEndX = e.changedTouches[0].screenX;
            touchEndY = e.changedTouches[0].screenY;
            
            // Odstranění vizuální zpětné vazby
            this.classList.remove('touch-active');
            
            // Zrušení časovače pro dlouhý stisk
            clearTimeout(longPressTimer);
            
            // Výpočet vzdálenosti pohybu
            const diffX = touchEndX - touchStartX;
            const diffY = touchEndY - touchStartY;
            
            // Detekce klepnutí (tap)
            if (Math.abs(diffX) < 10 && Math.abs(diffY) < 10) {
                const currentTime = new Date().getTime();
                const tapLength = currentTime - lastTapTime;
                
                // Detekce dvojitého klepnutí (double tap)
                if (tapLength < config.doubleTapDelay && tapLength > 0) {
                    // Akce pro dvojité klepnutí - např. otevření výběru souboru
                    simulateClick(document.getElementById(config.imageInputId));
                    e.preventDefault();
                }
                
                lastTapTime = currentTime;
            }
            
            // Detekce přejetí (swipe)
            if (Math.abs(diffX) > config.swipeThreshold) {
                if (diffX > 0) {
                    // Swipe doprava - např. vymazání obrázku
                    clearImage();
                } else {
                    // Swipe doleva - např. přepnutí na textový vstup
                    focusTextInput();
                }
            }
        }, { passive: false });
        
        // Zabránění výchozímu chování prohlížeče při pohybu prstu
        dropZone.addEventListener('touchmove', function(e) {
            // Zrušení časovače pro dlouhý stisk při pohybu
            clearTimeout(longPressTimer);
        }, { passive: true });
        
        // Zabránění výchozímu chování prohlížeče při opuštění prvku
        dropZone.addEventListener('touchcancel', function(e) {
            // Odstranění vizuální zpětné vazby
            this.classList.remove('touch-active');
            
            // Zrušení časovače pro dlouhý stisk
            clearTimeout(longPressTimer);
        }, { passive: true });
    }
    
    // Vylepšení pro textový vstup na dotykových zařízeních
    if (textInput && isTouchDevice) {
        // Optimalizace pro virtuální klávesnici
        textInput.addEventListener('focus', function() {
            // Posun obsahu nahoru, aby byl viditelný při otevřené klávesnici
            setTimeout(() => {
                window.scrollTo(0, this.getBoundingClientRect().top - 20);
            }, 300);
        });
        
        // Přidání tlačítka pro vymazání textu
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.className = 'clear-text-button';
        clearButton.innerHTML = '&times;';
        clearButton.style.display = 'none';
        
        // Vložení tlačítka vedle textového vstupu
        textInput.parentNode.insertBefore(clearButton, textInput.nextSibling);
        
        // Zobrazení/skrytí tlačítka podle obsahu
        textInput.addEventListener('input', function() {
            clearButton.style.display = this.value.length > 0 ? 'block' : 'none';
        });
        
        // Vymazání textu po kliknutí na tlačítko
        clearButton.addEventListener('click', function() {
            textInput.value = '';
            this.style.display = 'none';
            textInput.focus();
        });
    }
    
    // Vylepšení pro tlačítka na dotykových zařízeních
    if (submitButton && isTouchDevice) {
        // Zabránění vícenásobnému odeslání
        submitButton.addEventListener('touchstart', function(e) {
            // Vizuální zpětná vazba
            this.classList.add('touch-active');
            
            // Deaktivace tlačítka po kliknutí
            this.addEventListener('click', function() {
                this.disabled = true;
                this.classList.add('processing');
                
                // Obnovení tlačítka po dokončení zpracování (simulace)
                setTimeout(() => {
                    this.disabled = false;
                    this.classList.remove('processing');
                }, 3000);
            }, { once: true });
        });
        
        submitButton.addEventListener('touchend', function() {
            this.classList.remove('touch-active');
        });
    }
    
    // Vylepšení pro mobilní navigaci
    if (navToggle && navMenu && isTouchDevice) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            this.setAttribute('aria-expanded', 
                this.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
            );
        });
        
        // Zavření menu při kliknutí mimo
        document.addEventListener('click', function(e) {
            if (navMenu.classList.contains('active') && 
                !navMenu.contains(e.target) && 
                e.target !== navToggle) {
                navMenu.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Zavření menu při swipe doleva
        document.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });
        
        document.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            
            if (navMenu.classList.contains('active') && 
                touchStartX - touchEndX > config.swipeThreshold) {
                navMenu.classList.remove('active');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        }, { passive: true });
    }
    
    // Pomocné funkce
    function showTouchHelp(element) {
        // Vytvoření a zobrazení nápovědy pro dotykové ovládání
        const helpTooltip = document.createElement('div');
        helpTooltip.className = 'touch-help-tooltip';
        helpTooltip.textContent = 'Přetáhněte sem obrázek nebo klepněte pro výběr souboru';
        
        element.appendChild(helpTooltip);
        
        // Automatické odstranění nápovědy po 3 sekundách
        setTimeout(() => {
            helpTooltip.classList.add('fade-out');
            setTimeout(() => {
                element.removeChild(helpTooltip);
            }, 300);
        }, 3000);
    }
    
    function simulateClick(element) {
        if (!element) return;
        
        // Simulace kliknutí na element
        const event = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: true
        });
        
        element.dispatchEvent(event);
    }
    
    function clearImage() {
        if (!imagePreview) return;
        
        // Vymazání náhledu obrázku
        imagePreview.src = '';
        imagePreview.classList.add('hidden');
        
        // Vymazání vstupního pole pro soubor
        const imageInput = document.getElementById(config.imageInputId);
        if (imageInput) {
            imageInput.value = '';
        }
        
        // Skrytí tlačítek pro manipulaci s obrázkem
        const clearButton = document.getElementById('clearImageButton');
        const cropButton = document.getElementById('cropImageButton');
        
        if (clearButton) clearButton.classList.add('hidden');
        if (cropButton) cropButton.classList.add('hidden');
    }
    
    function focusTextInput() {
        if (!textInput) return;
        
        // Přepnutí na textový vstup
        textInput.focus();
        
        // Posun na textové pole
        textInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Optimalizace pro iOS Safari
    if (isTouchDevice && /iPad|iPhone|iPod/.test(navigator.userAgent)) {
        // Oprava problému s výškou viewportu na iOS
        const viewportMeta = document.querySelector('meta[name="viewport"]');
        if (viewportMeta) {
            viewportMeta.content = 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0';
        }
        
        // Oprava problému s 300ms zpožděním kliknutí na iOS
        document.addEventListener('touchend', function(e) {
            // Prevence výchozího chování pouze pro klikatelné prvky
            const target = e.target;
            if (target.tagName === 'A' || target.tagName === 'BUTTON' || 
                target.tagName === 'INPUT' || target.tagName === 'LABEL' ||
                target.classList.contains('clickable')) {
                e.preventDefault();
                
                // Simulace kliknutí
                setTimeout(() => {
                    simulateClick(target);
                }, 0);
            }
        }, { passive: false });
    }
});

/**
 * Poznámka: Pro plnou funkčnost tohoto kódu je potřeba přidat následující CSS třídy:
 * 
 * .touch-device - Přidáno k body elementu pro dotykové zařízení
 * .touch-active - Přidáno k prvkům při aktivním dotyku
 * .processing - Přidáno k tlačítkům během zpracování
 * .clear-text-button - Styl pro tlačítko vymazání textu
 * .touch-help-tooltip - Styl pro nápovědu při dlouhém stisku
 * .fade-out - Animace pro mizení prvků
 * 
 * Také je potřeba přidat následující HTML elementy nebo atributy:
 * 
 * - Tlačítko pro přepínání mobilní navigace s id="navToggle" a aria-expanded="false"
 * - Kontejner pro mobilní navigaci s id="navMenu"
 */
