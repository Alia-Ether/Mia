#╔══════════════════════════════════════════════════════════════════════════════════════╗
#║  Link: t.me/FrontendVSCode                                                           ║
#║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                                           ║
#║  lang: C / Makefile                                                                  ║
#║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                                                       ║
#║  build:3.10.15-termux-volt-fix                                                       ║
#║  files: Makefile                                                                     ║
#║                                                                                      ║
#║  ПОЛНАЯ АВТОМАТИЗАЦИЯ:                                                               ║
#║  - Устанавливает gcc и termux-api если нет                                          ║
#║  - Собирает C код                                                                   ║
#║  - Устанавливает в site-packages                                                    ║
#║  - Создаёт команду 'sofia' для глобального доступа                                  ║
#╚══════════════════════════════════════════════════════════════════════════════════════╝

# ==================== КОНФИГУРАЦИЯ ====================
CC = gcc
CFLAGS = -Wno-typedef-redefinition -Wno-implicit-function-declaration -Wno-macro-redefined -O2 -Wall -Wextra -Iinclude -D_GNU_SOURCE
LDFLAGS = -lm -lpthread
TARGET = sofia_monitor

# Пути для Termux
PREFIX = /data/data/com.termux/files/usr
PYTHON_VERSION = $(shell python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "3.10")
SITEPACKAGES = $(PREFIX)/lib/python$(PYTHON_VERSION)/site-packages
TARGET_DIR = $(SITEPACKAGES)/miaui_mi/security/pypass
BINDIR = $(PREFIX)/bin

# Исходные файлы
SOURCES = $(wildcard src/*.c)
OBJECTS = $(SOURCES:.c=.o)

# Цвета
RED = \033[91m
GREEN = \033[92m
YELLOW = \033[93m
CYAN = \033[96m
RESET = \033[0m
BOLD = \033[1m

# ==================== АВТОМАТИЧЕСКАЯ ПРОВЕРКА И УСТАНОВКА ЗАВИСИМОСТЕЙ ====================

.PHONY: check-deps install-deps
check-deps:
	@echo "$(CYAN)🔍 Проверка зависимостей...$(RESET)"
	@command -v gcc >/dev/null 2>&1 || { \
		echo "$(YELLOW)⚠️  gcc не найден, устанавливаю...$(RESET)"; \
		pkg install gcc make binutils -y; \
	}
	@command -v termux-battery-status >/dev/null 2>&1 || { \
		echo "$(YELLOW)⚠️  termux-api не установлен, устанавливаю...$(RESET)"; \
		pkg install termux-api -y; \
	}
	@echo "$(GREEN)✅ Все зависимости установлены$(RESET)"

# ==================== ОСНОВНЫЕ ЦЕЛИ ====================

all: check-deps check_dirs $(TARGET)
	@echo "$(GREEN)✅ Сборка завершена успешно!$(RESET)"
	@echo "$(CYAN)📦 Запусти: ./$(TARGET)$(RESET)"

check_dirs:
	@if [ ! -d "src" ]; then \
		echo "$(RED)❌ Ошибка: папка src не найдена!$(RESET)"; \
		exit 1; \
	fi
	@if [ ! -d "include" ]; then \
		echo "$(RED)❌ Ошибка: папка include не найдена!$(RESET)"; \
		exit 1; \
	fi

$(TARGET): $(OBJECTS)
	@echo "$(CYAN)🔨 Компиляция $(TARGET)...$(RESET)"
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJECTS) $(LDFLAGS)
	@echo "$(GREEN)✅ Готово: $(TARGET)$(RESET)"

%.o: %.c
	@echo "$(YELLOW)⚙️  Компиляция $<...$(RESET)"
	$(CC) $(CFLAGS) -c $< -o $@

# ==================== ПОЛНАЯ УСТАНОВКА (ВСЁ АВТОМАТОМ) ====================

install: all
	@echo "$(CYAN)📦 Полная установка SOFIA Monitor...$(RESET)"
	
	# Создаём директории
	@mkdir -p $(TARGET_DIR)
	@mkdir -p $(BINDIR)
	
	# Копируем бинарник
	cp $(TARGET) $(TARGET_DIR)/
	chmod 755 $(TARGET_DIR)/$(TARGET)
	@echo "$(GREEN)✅ Бинарник установлен: $(TARGET_DIR)/$(TARGET)$(RESET)"
	
	# Создаём команду sofia
	@echo '#!/data/data/com.termux/files/usr/bin/bash' > $(BINDIR)/sofia
	@echo '$(TARGET_DIR)/$(TARGET) "$$@"' >> $(BINDIR)/sofia
	chmod 755 $(BINDIR)/sofia
	@echo "$(GREEN)✅ Команда 'sofia' создана: $(BINDIR)/sofia$(RESET)"
	
	# Копируем Python лаунчер (если есть)
	@if [ -f "launcher.py" ]; then \
		cp launcher.py $(TARGET_DIR)/; \
		chmod 755 $(TARGET_DIR)/launcher.py; \
		echo "$(GREEN)✅ Лаунчер установлен$(RESET)"; \
	fi
	
	# Создаём алиас в .bashrc для макс. удобства
	@if ! grep -q "alias sofia=" ~/.bashrc 2>/dev/null; then \
		echo 'alias sofia="$(BINDIR)/sofia"' >> ~/.bashrc; \
		echo "$(GREEN)✅ Алиас добавлен в ~/.bashrc$(RESET)"; \
	fi
	
	# Очищаем кэш
	hash -r 2>/dev/null || true
	
	@echo ""
	@echo "$(GREEN)🎉 УСТАНОВКА ЗАВЕРШЕНА!$(RESET)"
	@echo ""
	@echo "$(BOLD)📦 Теперь вы можете использовать:$(RESET)"
	@echo "   $(CYAN)sofia$(RESET)     - интерактивный монитор"
	@echo "   $(CYAN)sofia -j$(RESET)  - JSON вывод"
	@echo "   $(CYAN)sofia -i$(RESET)  - информация об устройстве"
	@echo "   $(CYAN)sofia -n$(RESET)  - сетевая информация"
	@echo "   $(CYAN)sofia -h$(RESET)  - справка"
	@echo ""
	@echo "$(BOLD)🔄 Перезагрузите терминал или выполните:$(RESET)"
	@echo "   $(CYAN)source ~/.bashrc$(RESET)"
	@echo "   $(CYAN)exec bash$(RESET)"

# ==================== ТОЛЬКО ДЛЯ РАЗРАБОТКИ (pip install вариант) ====================

pip-install:
	@echo "$(CYAN)📦 Подготовка к pip install...$(RESET)"
	@mkdir -p miaui_mi/security/pypass
	@cp -r src/ miaui_mi/security/pypass/
	@cp -r include/ miaui_mi/security/pypass/
	@cp Makefile miaui_mi/security/pypass/
	@cp launcher.py miaui_mi/security/pypass/ 2>/dev/null || true
	@echo "$(GREEN)✅ Готово для pip install$(RESET)"
	@echo "   Запустите: pip install ."

# ==================== ОЧИСТКА ====================

clean:
	@echo "$(YELLOW)🧹 Очистка...$(RESET)"
	rm -f $(OBJECTS) $(TARGET)
	@echo "$(GREEN)✅ Готово$(RESET)"

clean-all: clean
	@echo "$(YELLOW)🧹 Полная очистка...$(RESET)"
	rm -rf miaui_mi/
	@echo "$(GREEN)✅ Готово$(RESET)"

# ==================== УДАЛЕНИЕ ====================

uninstall:
	@echo "$(RED)🗑️  Удаление...$(RESET)"
	rm -f $(TARGET_DIR)/$(TARGET)
	rm -f $(BINDIR)/sofia
	rm -rf $(TARGET_DIR)
	@echo "$(GREEN)✅ Удалено$(RESET)"

# ==================== ИНФОРМАЦИЯ ====================

info:
	@echo "$(CYAN)📊 SOFIA Monitor Information:$(RESET)"
	@echo "  Компилятор:     $(CC)"
	@echo "  Python версия:  $(PYTHON_VERSION)"
	@echo "  Установка:      $(TARGET_DIR)"
	@echo "  Команда:        $(BINDIR)/sofia"
	@echo "  Исходники:      $(words $(SOURCES)) файлов"

# ==================== HELP ====================

help:
	@echo "$(BOLD)$(CYAN)════════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(BOLD)$(GREEN)🔧 SOFIA MONITOR — УСТАНОВКА И ИСПОЛЬЗОВАНИЕ$(RESET)"
	@echo "$(BOLD)$(CYAN)════════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(YELLOW)📦 УСТАНОВКА:$(RESET)"
	@echo "   pip install Mia"
	@echo "   или вручную: make && sudo make install"
	@echo ""
	@echo "$(YELLOW)🚀 ЗАПУСК:$(RESET)"
	@echo "   sofia              - интерактивный режим"
	@echo "   sofia -j           - JSON вывод (30+ пунктов)"
	@echo "   sofia -i           - информация об устройстве"
	@echo "   sofia -n           - сетевая информация"
	@echo "   sofia -c           - камеры"
	@echo "   sofia -s           - датчики"
	@echo "   sofia -d           - детальный CPU"
	@echo "   sofia -h           - справка"
	@echo ""
	@echo "$(YELLOW)🛠️  КОМАНДЫ MAKE:$(RESET)"
	@echo "   make               - собрать"
	@echo "   make install       - собрать + установить"
	@echo "   make uninstall     - удалить"
	@echo "   make clean         - очистить объектные файлы"
	@echo "   make info          - показать информацию"
	@echo "   make help          - эта справка"
	@echo ""
	@echo "$(BOLD)$(CYAN)════════════════════════════════════════════════════════════════$(RESET)"

# ==================== ПО УМОЛЧАНИЮ ====================

.DEFAULT_GOAL := help

.PHONY: all clean install uninstall check-deps info help pip-install clean-all