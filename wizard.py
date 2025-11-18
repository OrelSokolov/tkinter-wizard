# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import threading
from abc import ABC, abstractmethod
from enum import Enum


class StepStatus(Enum):
    """Статус шага"""
    PENDING = "pending"  # Ожидает выполнения
    RUNNING = "running"  # Процесс выполняется
    SUCCESS = "success"  # Успешно завершен
    FAILED = "failed"    # Завершен с ошибкой


class ProgressInterface(ABC):
    """Интерфейс для работы с прогресс-баром"""
    
    @abstractmethod
    def set_percent(self, percent):
        """Установить процент выполнения (0-100)"""
        pass
    
    @abstractmethod
    def set_eta(self, seconds):
        """Установить оставшееся время (в секундах)"""
        pass
    
    @abstractmethod
    def set_elapsed_time(self, seconds):
        """Установить прошедшее время (в секундах)"""
        pass


class ProgressBarAdapter(ProgressInterface):
    """Адаптер для ttk.Progressbar с дополнительной информацией"""
    
    def __init__(self, progressbar, progress_var=None, percent_label=None, eta_label=None, elapsed_label=None):
        self.progressbar = progressbar
        self.progress_var = progress_var
        self.percent_label = percent_label
        self.eta_label = eta_label
        self.elapsed_label = elapsed_label
        self.start_time = time.time()
    
    def reset_start_time(self):
        """Сбросить время начала (вызывается при старте процесса)"""
        self.start_time = time.time()
    
    def set_percent(self, percent):
        """Установить процент выполнения"""
        try:
            if self.progress_var:
                self.progress_var.set(percent)
            elif self.progressbar:
                try:
                    self.progressbar['value'] = percent
                except tk.TclError:
                    pass  # Виджет уничтожен
            
            if self.percent_label:
                try:
                    self.percent_label.config(text="{}%".format(int(percent)))
                except tk.TclError:
                    pass  # Виджет уничтожен
        except:
            pass  # Виджеты могли быть уничтожены
    
    def set_eta(self, seconds):
        """Установить оставшееся время"""
        if self.eta_label:
            try:
                if seconds is not None and seconds > 0:
                    minutes = int(seconds // 60)
                    secs = int(seconds % 60)
                    self.eta_label.config(text="Осталось: {:02d}:{:02d}".format(minutes, secs))
                else:
                    self.eta_label.config(text="Осталось: --:--")
            except tk.TclError:
                pass  # Виджет уничтожен
    
    def set_elapsed_time(self, seconds):
        """Установить прошедшее время"""
        if self.elapsed_label:
            try:
                minutes = int(seconds // 60)
                secs = int(seconds % 60)
                self.elapsed_label.config(text="Прошло: {}:{}".format(minutes, secs))
            except tk.TclError:
                pass  # Виджет уничтожен
    
    def get_elapsed(self):
        """Получить прошедшее время с начала"""
        return time.time() - self.start_time


class WizardProcess:
    """
    Абстракция для процесса, который выполняется в шаге wizard'а.
    
    Принимает либо ProgressInterface для отображения прогресса,
    либо IO объект (например, TextArea) для логирования.
    
    Процесс выполняется в отдельном потоке и может быть отменен.
    """
    
    def __init__(self, progress_interface=None, logger=None, state_callback=None, root=None):
        """
        Args:
            progress_interface: объект, реализующий ProgressInterface
            logger: объект для логирования (например, ScrolledText)
            state_callback: функция для обновления состояния (разрешает переход)
            root: корневое окно Tkinter (для root.after)
        """
        self.progress_interface = progress_interface
        self.logger = logger
        self.state_callback = state_callback
        self.root = root
        self.success = True  # По умолчанию успешно
        self.start_time = None
        self._cancelled = False
        self._thread = None
        self._lock = threading.Lock()
    
    def is_cancelled(self):
        """Проверить, был ли процесс отменен"""
        with self._lock:
            return self._cancelled
    
    def cancel(self):
        """Отменить выполнение процесса"""
        with self._lock:
            self._cancelled = True
        # Если процесс завершился с отменой, устанавливаем неудачу
        if self.state_callback:
            self.state_callback(False)
    
    def log(self, message):
        """Вывести сообщение в лог"""
        if self.logger and not self.is_cancelled():
            try:
                self.logger.insert(tk.END, message + "\n")
                self.logger.see(tk.END)
                self.logger.update()
            except:
                pass  # Виджет мог быть уничтожен
    
    def update_progress(self, percent, eta=None):
        """Обновить прогресс (вызывается из потока процесса)"""
        if self.is_cancelled():
            return
        
        if self.progress_interface:
            # Обновляем UI через root.after в главном потоке
            if self.root:
                def update_ui():
                    if not self.is_cancelled() and self.progress_interface:
                        try:
                            self.progress_interface.set_percent(percent)
                            
                            # Всегда обновляем ETA (если передан или вычисляем автоматически)
                            if eta is not None:
                                self.progress_interface.set_eta(eta)
                            elif percent > 0 and percent < 100:
                                # Вычисляем ETA автоматически если не передан
                                if hasattr(self.progress_interface, 'get_elapsed'):
                                    elapsed = self.progress_interface.get_elapsed()
                                    if elapsed > 0:
                                        total_time = (elapsed / percent) * 100
                                        remaining = total_time - elapsed
                                        self.progress_interface.set_eta(remaining)
                            
                            # Обновляем прошедшее время
                            if hasattr(self.progress_interface, 'get_elapsed'):
                                elapsed = self.progress_interface.get_elapsed()
                                self.progress_interface.set_elapsed_time(elapsed)
                        except:
                            pass  # Виджеты могли быть уничтожены
                
                self.root.after(0, update_ui)
    
    def run(self):
        """
        Запустить процесс. Должен быть переопределен в наследниках.
        По умолчанию завершается успешно без действий.
        
        Этот метод выполняется в отдельном потоке.
        """
        self.start_time = time.time()
        # По умолчанию ничего не делаем, завершаем успешно
        if not self.is_cancelled() and self.state_callback:
            if self.root:
                self.root.after(0, lambda: self.state_callback(self.success))
            else:
                self.state_callback(self.success)
    
    def start(self):
        """Запустить процесс в отдельном потоке"""
        if self._thread is not None and self._thread.is_alive():
            return  # Поток уже запущен
        
        self._cancelled = False
        self._thread = threading.Thread(target=self._run_wrapper, daemon=True)
        self._thread.start()
    
    def _run_wrapper(self):
        """Обертка для выполнения run() в потоке"""
        try:
            self.run()
        except:
            # В случае ошибки завершаем неудачно
            if not self.is_cancelled() and self.state_callback:
                if self.root:
                    self.root.after(0, lambda: self.state_callback(False))
                else:
                    self.state_callback(False)
    
    def wait(self, timeout=None):
        """Дождаться завершения процесса"""
        if self._thread:
            self._thread.join(timeout)
    
    def set_success(self, success):
        """Установить статус выполнения и уведомить callback"""
        if self.is_cancelled():
            return  # Если отменен, не меняем статус
        
        self.success = success
        if self.state_callback:
            if self.root:
                self.root.after(0, lambda: self.state_callback(success))
            else:
                self.state_callback(success)


class WizardStep(ABC):
    """
    Абстрактный класс для шага wizard'а.
    Программист создает наследники этого класса для своих шагов.
    """
    
    def __init__(self, wizard_app):
        self.wizard_app = wizard_app
        self.content_frame = None
        self.status = StepStatus.PENDING
        self.process = None
    
    @abstractmethod
    def create_content(self, content_frame):
        """
        Создать содержимое шага. Переопределяется программистом.
        
        Args:
            content_frame: фрейм, в который нужно разместить виджеты шага
        """
        pass
    
    @abstractmethod
    def create_process(self):
        """
        Создать процесс для этого шага. Переопределяется программистом.
        
        Returns:
            WizardProcess или None, если процесс не нужен
        """
        pass
    
    def render(self, content_frame):
        """Отрендерить шаг (вызывается WizardApp)"""
        self.content_frame = content_frame
        self.create_content(content_frame)
        
        # Создаем процесс, если он есть
        self.process = self.create_process()
        if self.process:
            # Устанавливаем root для процесса, если он еще не установлен
            if not self.process.root:
                self.process.root = self.wizard_app.root
            # Запускаем процесс в отдельном потоке
            self.status = StepStatus.RUNNING
            self.process.start()
    
    def _on_process_complete(self, success):
        """Callback, вызываемый когда процесс завершился"""
        if success:
            self.status = StepStatus.SUCCESS
        else:
            self.status = StepStatus.FAILED
        
        # Уведомляем wizard_app об изменении статуса
        self.wizard_app.on_step_status_changed(self)
    
    def can_proceed(self):
        """Можно ли перейти к следующему шагу"""
        # Если нет процесса, можно сразу переходить
        if not self.process:
            return True
        
        # Если процесс завершился успешно, можно переходить
        return self.status == StepStatus.SUCCESS
    
    def is_failed(self):
        """Завершился ли шаг с ошибкой"""
        return self.status == StepStatus.FAILED


class WizardApp:
    """
    Главный класс wizard'а. Стандартный компонент, который не меняется.
    Собирается из WizardStep'ов.
    """
    
    def __init__(self, root, steps=None):
        """
        Args:
            root: корневое окно Tkinter
            steps: список WizardStep'ов (можно установить позже через set_steps)
        """
        self.root = root
        self.root.title("Установщик - Wizard Demo")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # Настройка стилей с использованием системной темы
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        
        # Выбираем системную тему Windows, если доступна
        if 'vista' in available_themes:
            self.style.theme_use('vista')
        elif 'winnative' in available_themes:
            self.style.theme_use('winnative')
        elif 'xpnative' in available_themes:
            self.style.theme_use('xpnative')
        else:
            if available_themes:
                self.style.theme_use(available_themes[0])
        
        self.steps = steps or []
        self.current_step_index = 0
        
        # Создание контейнера для шагов
        self.content_frame = tk.Frame(self.root, padx=20, pady=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки навигации
        self.nav_frame = tk.Frame(self.root, padx=20, pady=10)
        self.nav_frame.pack(fill=tk.X)
        
        self.back_btn = ttk.Button(self.nav_frame, text="< Назад", 
                                   command=self.prev_step, state="disabled")
        self.back_btn.pack(side=tk.LEFT)
        
        self.next_btn = ttk.Button(self.nav_frame, text="Далее >", 
                                   command=self.next_step)
        self.next_btn.pack(side=tk.RIGHT)
        
        self.cancel_btn = ttk.Button(self.nav_frame, text="Отмена", 
                                     command=self.cancel_process)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Отображение первого шага (если шаги уже есть)
        if self.steps:
            self.show_current_step()
    
    def set_steps(self, steps):
        """Установить шаги wizard'а"""
        self.steps = steps
        self.current_step_index = 0
        if self.steps:
            self.show_current_step()
    
    def clear_content(self):
        """Очистить содержимое текущего шага"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_current_step(self):
        """Показать текущий шаг"""
        self.clear_content()
        
        if 0 <= self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            step.render(self.content_frame)
        
        self.update_navigation()
    
    def update_navigation(self):
        """Обновить состояние кнопок навигации"""
        current_step = None
        if 0 <= self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]
        
        # Если это завершающий шаг с ошибкой, скрываем все кнопки
        if isinstance(current_step, ErrorCompletionStep):
            self.back_btn.pack_forget()
            self.next_btn.pack_forget()
            self.cancel_btn.pack_forget()
            return
        
        # Если это завершающий шаг успешного завершения, скрываем "Назад" и "Отмена"
        if isinstance(current_step, SuccessCompletionStep):
            self.back_btn.pack_forget()
            self.cancel_btn.pack_forget()
            # Оставляем только кнопку "Завершить"
            try:
                self.next_btn.pack(side=tk.RIGHT)
            except:
                pass
            self.next_btn.config(text="Завершить", command=self.root.quit)
            self.next_btn.config(state="normal")
            return
        
        # Убеждаемся, что кнопки видны (если были скрыты ранее)
        try:
            self.back_btn.pack(side=tk.LEFT)
        except:
            pass
        try:
            self.next_btn.pack(side=tk.RIGHT)
        except:
            pass
        try:
            self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        except:
            pass
        
        # Кнопка "Назад" - блокируем если процесс выполняется
        if self.current_step_index == 0:
            self.back_btn.config(state="disabled")
        elif current_step and current_step.status == StepStatus.RUNNING:
            # Блокируем "Назад" во время выполнения процесса
            self.back_btn.config(state="disabled")
        else:
            self.back_btn.config(state="normal")
        
        # Кнопка "Далее"
        if self.current_step_index >= len(self.steps) - 1:
            self.next_btn.config(text="Завершить", command=self.root.quit)
            self.next_btn.config(state="normal")
        else:
            current_step = self.steps[self.current_step_index]
            
            # Проверяем, может ли процесс перейти к следующему шагу
            if current_step.can_proceed():
                self.next_btn.config(text="Далее >", command=self.next_step)
                self.next_btn.config(state="normal")
            else:
                # Процесс еще не завершен, блокируем кнопку
                self.next_btn.config(text="Далее >", command=self.next_step)
                self.next_btn.config(state="disabled")
    
    def on_step_status_changed(self, step):
        """Вызывается когда статус шага изменился"""
        # Проверяем, если шаг завершился с ошибкой, показываем ошибку
        if step.is_failed():
            # Добавляем ErrorCompletionStep в конец списка шагов, если его еще нет
            has_error_step = any(isinstance(s, ErrorCompletionStep) for s in self.steps)
            if not has_error_step:
                error_step = ErrorCompletionStep(self)
                self.steps.append(error_step)
            
            # Переходим к шагу с ошибкой
            for i, s in enumerate(self.steps):
                if isinstance(s, ErrorCompletionStep):
                    self.current_step_index = i
                    self.show_current_step()
                    return
        
        # Обновляем навигацию
        self.update_navigation()
    
    def cancel_process(self):
        """Отменить текущий процесс и завершить wizard с ошибкой"""
        current_step = None
        if 0 <= self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]
        
        # Отменяем процесс текущего шага, если он выполняется
        if current_step and current_step.process:
            current_step.process.cancel()
        
        # Закрываем wizard
        self.root.quit()
    
    def next_step(self):
        """Перейти к следующему шагу"""
        current_step = self.steps[self.current_step_index]
        
        # Проверяем, можно ли перейти
        if not current_step.can_proceed():
            return
        
        # Если шаг завершился с ошибкой, переходим на ErrorCompletionStep
        if current_step.is_failed():
            # Добавляем ErrorCompletionStep в конец списка шагов, если его еще нет
            has_error_step = any(isinstance(s, ErrorCompletionStep) for s in self.steps)
            if not has_error_step:
                error_step = ErrorCompletionStep(self)
                self.steps.append(error_step)
            
            # Переходим к шагу с ошибкой
            for i, s in enumerate(self.steps):
                if isinstance(s, ErrorCompletionStep):
                    self.current_step_index = i
                    self.show_current_step()
                    return
        
        # Переходим к следующему шагу
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self.show_current_step()
    
    def prev_step(self):
        """Вернуться к предыдущему шагу"""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.show_current_step()


# ============================================================================
# Примеры конкретных шагов (создаются программистом)
# ============================================================================

class WelcomeStep(WizardStep):
    """Шаг приветствия"""
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Добро пожаловать!", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20))
        
        message = tk.Label(content_frame, 
                          text="Этот мастер поможет вам установить программу.\n\n"
                               "Нажмите 'Далее' чтобы продолжить.",
                          justify=tk.LEFT, font=("Arial", 10))
        message.pack(pady=10)
        
        icon_label = tk.Label(content_frame, text="☺", font=("Arial", 48))
        icon_label.pack(pady=30)
    
    def create_process(self):
        # Нет процесса, можно сразу переходить
        return None


class ConfigurationStep(WizardStep):
    """Шаг конфигурации"""
    
    def __init__(self, wizard_app):
        super().__init__(wizard_app)
        self.config_choice = tk.StringVar(value="standard")
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Конфигурация", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20), anchor=tk.W)
        
        info = tk.Label(content_frame, 
                       text="Выберите тип установки:",
                       justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 15))
        
        radio_frame = tk.Frame(content_frame)
        radio_frame.pack(anchor=tk.W, fill=tk.X, padx=20)
        
        ttk.Radiobutton(radio_frame, text="Стандартная установка", 
                       variable=self.config_choice, value="standard").pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(radio_frame, text="Минимальная установка", 
                       variable=self.config_choice, value="minimal").pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(radio_frame, text="Полная установка", 
                       variable=self.config_choice, value="full").pack(anchor=tk.W, pady=5)
    
    def create_process(self):
        return None


class ProgressStep(WizardStep):
    """Шаг с прогресс-баром"""
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Подготовка к установке", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20), anchor=tk.W)
        
        info = tk.Label(content_frame, 
                       text="Пожалуйста, подождите...",
                       justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 15))
        
        # Создаем progressbar и метки
        progress_frame = tk.Frame(content_frame)
        progress_frame.pack(fill=tk.X, pady=20)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, 
                                       variable=progress_var,
                                       maximum=100, length=500)
        progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        labels_frame = tk.Frame(progress_frame)
        labels_frame.pack(fill=tk.X)
        
        percent_label = tk.Label(labels_frame, text="0%", font=("Arial", 10))
        percent_label.pack(side=tk.LEFT)
        
        eta_label = tk.Label(labels_frame, text="Осталось: --:--", 
                            font=("Arial", 9), fg="gray")
        eta_label.pack(side=tk.LEFT, padx=(20, 0))
        
        elapsed_label = tk.Label(labels_frame, text="Прошло: 0:00", 
                                font=("Arial", 9), fg="gray")
        elapsed_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Сохраняем ссылки для использования в процессе
        self.progress_bar = progress_bar
        self.progress_var = progress_var
        self.percent_label = percent_label
        self.eta_label = eta_label
        self.elapsed_label = elapsed_label
    
    def create_process(self):
        # Создаем адаптер для progressbar
        progress_interface = ProgressBarAdapter(
            self.progress_bar,
            progress_var=self.progress_var,
            percent_label=self.percent_label,
            eta_label=self.eta_label,
            elapsed_label=self.elapsed_label
        )
        
        # Создаем процесс
        process = ProgressProcess(
            progress_interface=progress_interface,
            state_callback=self._on_process_complete
        )
        
        return process


class ProgressProcess(WizardProcess):
    """Процесс с прогресс-баром"""
    
    def run(self):
        """Симулировать установку с прогрессом (выполняется в отдельном потоке)"""
        self.start_time = time.time()
        
        # Сбрасываем время начала в progress_interface
        if self.progress_interface and hasattr(self.progress_interface, 'reset_start_time'):
            self.progress_interface.reset_start_time()
        
        # Симулируем установку с проверкой отмены
        while not self.is_cancelled():
            elapsed = time.time() - self.start_time
            percent = min((elapsed / 3.0) * 100, 100)  # 3 секунды на установку
            
            # Вычисляем ETA
            if percent < 100 and percent > 0:
                # Вычисляем оставшееся время на основе текущей скорости
                remaining = (100 - percent) * (elapsed / percent)
            elif percent >= 100:
                remaining = 0
            else:
                # В начале можно использовать примерное время (3 секунды)
                remaining = 3.0
            
            self.update_progress(percent, remaining)
            
            if percent >= 100:
                # Завершаем успешно
                if not self.is_cancelled():
                    self.set_success(True)
                break
            
            # Спим немного перед следующей итерацией
            time.sleep(0.03)
        
        # Если отменено, завершаем неудачно
        if self.is_cancelled():
            self.set_success(False)


class CheckboxStep(WizardStep):
    """Шаг с чекбоксом для выбора ошибки"""
    
    def __init__(self, wizard_app):
        super().__init__(wizard_app)
        self.error_checkbox = tk.BooleanVar(value=False)
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Проверка системы", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20), anchor=tk.W)
        
        info = tk.Label(content_frame, 
                       text="Отметьте опцию ниже, чтобы симулировать ошибку:",
                       justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 15))
        
        checkbox_frame = tk.Frame(content_frame)
        checkbox_frame.pack(anchor=tk.W, fill=tk.X, padx=20)
        
        ttk.Checkbutton(checkbox_frame, 
                       text="Вызвать ошибку при установке", 
                       variable=self.error_checkbox).pack(anchor=tk.W, pady=5)
        
        warning = tk.Label(content_frame, 
                          text="(Если не отмечено, установка будет успешной)",
                          font=("Arial", 9), fg="gray")
        warning.pack(anchor=tk.W, padx=20, pady=(5, 0))
    
    def create_process(self):
        return None


class LogsStep(WizardStep):
    """Шаг с логами"""
    
    def create_content(self, content_frame):
        # Проверяем, была ли выбрана ошибка в предыдущем шаге ДО создания контента
        checkbox_step = None
        for step in self.wizard_app.steps:
            if isinstance(step, CheckboxStep):
                checkbox_step = step
                break
        
        self.should_fail = checkbox_step and checkbox_step.error_checkbox.get()
        
        # Если должна быть ошибка, не показываем консоль, процесс завершится сразу
        if self.should_fail:
            title = tk.Label(content_frame, text="Проверка установки", 
                            font=("Arial", 16, "bold"))
            title.pack(pady=(0, 20), anchor=tk.W)
            
            info = tk.Label(content_frame, 
                           text="Проверка статуса установки...",
                           justify=tk.LEFT, font=("Arial", 10))
            info.pack(anchor=tk.W, pady=(0, 15))
            return
        
        title = tk.Label(content_frame, text="Установка", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 15), anchor=tk.W)
        
        info = tk.Label(content_frame, 
                       text="Выполняется установка...",
                       justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 10))
        
        # Текстовое поле для логов
        self.log_text = scrolledtext.ScrolledText(content_frame, 
                                                  height=15, 
                                                  width=70,
                                                  font=("Consolas", 9),
                                                  bg="black",
                                                  fg="green",
                                                  insertbackground="green")
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def create_process(self):
        # Если должна быть ошибка, создаем процесс который сразу завершится с ошибкой
        if self.should_fail:
            process = LogsProcess(
                logger=None,  # Нет логгера, т.к. консоль не показывается
                state_callback=self._on_process_complete,
                should_fail=True
            )
            return process
        
        # Создаем процесс логирования
        process = LogsProcess(
            logger=self.log_text,
            state_callback=self._on_process_complete,
            should_fail=False
        )
        
        return process


class LogsProcess(WizardProcess):
    """Процесс с логированием"""
    
    def __init__(self, logger, state_callback, should_fail=False):
        super().__init__(logger=logger, state_callback=state_callback)
        self.should_fail = should_fail
        self.logs = [
            "[INFO] Инициализация установки...",
            "[INFO] Проверка системных требований...",
            "[OK] Системные требования соответствуют",
            "[INFO] Подготовка файлов...",
            "[INFO] Копирование файлов в целевую директорию...",
            "[OK] Файлы скопированы успешно",
            "[INFO] Создание реестровых записей...",
            "[OK] Реестр обновлен",
            "[INFO] Регистрация служб...",
            "[OK] Службы зарегистрированы",
            "[INFO] Создание ярлыков...",
            "[OK] Ярлыки созданы",
            "[INFO] Обновление переменных окружения...",
            "[OK] Переменные окружения обновлены",
            "[INFO] Завершение установки...",
        ]
    
    def run(self):
        """Стриминг логов (выполняется в отдельном потоке)"""
        self.start_time = time.time()
        
        # Если должна быть ошибка и нет логгера, сразу завершаемся с ошибкой
        if self.should_fail and not self.logger:
            time.sleep(0.1)  # Небольшая задержка
            if not self.is_cancelled():
                self.set_success(False)
            return
        
        # Выводим логи построчно с проверкой отмены
        for log in self.logs:
            if self.is_cancelled():
                break
            
            self.log(log)
            time.sleep(0.5)  # Задержка между логами
        
        # Все логи добавлены
        if not self.is_cancelled():
            if self.should_fail:
                self.log("[ERROR] Установка завершена с ошибкой!")
                self.set_success(False)
            else:
                self.log("[SUCCESS] Установка завершена успешно!")
                self.set_success(True)
        
        # Если отменено, завершаем неудачно
        if self.is_cancelled():
            self.set_success(False)


class ErrorCompletionStep(WizardStep):
    """Шаг завершения с ошибкой"""
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Установка завершена с ошибками", 
                        font=("Arial", 16, "bold"), fg="red")
        title.pack(pady=(0, 20))
        
        icon_label = tk.Label(content_frame, text="✗", 
                             font=("Arial", 48), fg="red")
        icon_label.pack(pady=20)
        
        message = tk.Label(content_frame, 
                          text="Произошла ошибка во время установки.\n"
                               "Установка не была завершена успешно.",
                          justify=tk.CENTER, font=("Arial", 10))
        message.pack(pady=10)
    
    def create_process(self):
        return None


class SuccessCompletionStep(WizardStep):
    """Шаг успешного завершения"""
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Установка завершена успешно!", 
                        font=("Arial", 16, "bold"), fg="green")
        title.pack(pady=(0, 20))
        
        icon_label = tk.Label(content_frame, text="✓", 
                             font=("Arial", 48), fg="green")
        icon_label.pack(pady=20)
        
        message = tk.Label(content_frame, 
                          text="Программа была успешно установлена на ваш компьютер.\n"
                               "Нажмите 'Завершить' чтобы закрыть мастер установки.",
                          justify=tk.CENTER, font=("Arial", 10))
        message.pack(pady=10)
        
        # Получаем выбранную конфигурацию
        config_name = "Неизвестно"
        for step in self.wizard_app.steps:
            if isinstance(step, ConfigurationStep):
                configs = {
                    "standard": "Стандартная установка",
                    "minimal": "Минимальная установка",
                    "full": "Полная установка"
                }
                config_name = configs.get(step.config_choice.get(), "Неизвестно")
                break
        
        summary = tk.Label(content_frame, 
                          text="Выбранная конфигурация: {}".format(config_name),
                          justify=tk.CENTER, font=("Arial", 9), fg="gray")
        summary.pack(pady=(10, 0))
    
    def create_process(self):
        return None


def main():
    root = tk.Tk()
    
    # Создаем wizard сначала (без шагов)
    wizard = WizardApp(root)
    
    # Создаем шаги wizard'а (передаем wizard_app)
    steps = [
        WelcomeStep(wizard),
        ConfigurationStep(wizard),
        ProgressStep(wizard),
        CheckboxStep(wizard),
        LogsStep(wizard),
        SuccessCompletionStep(wizard),
    ]
    
    # Устанавливаем шаги в wizard
    wizard.set_steps(steps)
    
    root.mainloop()


if __name__ == "__main__":
    main()
