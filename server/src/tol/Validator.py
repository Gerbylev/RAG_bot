import re

from bot.template import t


class Validator:
    def __init__(self, value):
        self.value = value
        self.error_message = ""

    def is_not_none(self):
        """Проверяет, что значение не None."""
        if self.value is None:
            self.error_message = "Значение не должно быть None."
            return False
        return True

    def check_length(self, min_length: int = None, max_length: int = None):
        """Проверяет, что длина строки находится в указанном диапазоне."""
        if self.value is None:
            self.error_message = "Значение не должно быть None."
            return False
        length = len(self.value)
        if min_length is not None and length < min_length:
            self.error_message = f"Длина должна быть не меньше {min_length} символов."
            return False
        if max_length is not None and length > max_length:
            self.error_message = f"Длина должна быть не больше {max_length} символов."
            return False
        return True

    def check_number_range(self, min_val: float, max_val: float):
        """
        Проверяет, что строка может быть преобразована в число и находится в диапазоне [min_val, max_val].
        Дополнительно проверяет, что строка содержит только число.
        """
        if self.value is None:
            self.error_message = "Значение не должно быть None."
            return False

        number_pattern = r'^[-+]?\d+(\.\d+)?$'
        if not re.fullmatch(number_pattern, self.value.strip()):
            self.error_message = "Строка должна содержать только число."
            return False

        try:
            num = float(self.value)
        except ValueError:
            self.error_message = "Ошибка преобразования строки в число."
            return False

        if not (min_val <= num <= max_val):
            self.error_message = f"Число должно быть в диапазоне от {min_val} до {max_val}."
            return False
        return True

    def is_numeric(self):
        """
        Проверяет, что строка содержит только число (целое или с плавающей точкой).
        """
        if self.value is None:
            self.error_message = "Значение не должно быть None."
            return False
        number_pattern = r'^[-+]?\d+(\.\d+)?$'
        if not re.fullmatch(number_pattern, self.value.strip()):
            self.error_message = "Строка должна содержать только число."
            return False
        return True

    def is_email(self):
        """
        Проверяет, что строка соответствует шаблону email.
        Используется простое регулярное выражение.
        """
        if self.value is None:
            self.error_message = "Значение не должно быть None."
            return False
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.fullmatch(email_pattern, self.value.strip()):
            self.error_message = "Неверный формат email."
            return False
        return True

    def check_regex(self, pattern: str):
        """
        Проверяет, что строка соответствует заданному регулярному выражению.
        """
        if self.value is None:
            self.error_message = "Значение не должно быть None."
            return False
        if not re.fullmatch(pattern, self.value.strip()):
            self.error_message = "Строка не соответствует шаблону."
            return False
        return True

    def execute_validation(self, method_call: str):
        """
        Выполняет валидацию по строке вида "is_numeric()" или "check_length(0, 10)".
        Если проверка не проходит, в self.error_message сохраняется сообщение об ошибке.
        """
        if method_call is None:
            return True

        if self.value == t.skip:
            return True

        try:
            # Разбираем строку, например "check_length(0, 10)"
            method_name, _, args = method_call.partition("(")
            args = args.rstrip(")")

            # Получаем метод по имени
            method = getattr(self, method_name, None)
            if method is None or not callable(method):
                # Добавить log
                self.error_message = f"Метод '{method_name}' не найден."
                return True

            # Преобразуем аргументы в кортеж (используем eval - применяйте осторожно, если данные не из доверенного источника)
            parsed_args = eval(f"({args})") if args else ()
            result = method(*parsed_args) if isinstance(parsed_args, tuple) else method(parsed_args)
            if not result and not self.error_message:
                self.error_message = "Неизвестная ошибка валидации."
            return result

        except Exception as e:
            self.error_message = f"Ошибка при выполнении валидации: {e}"
            return True

# # Примеры использования
if __name__ == '__main__':
    # Пример 1: Проверка на not None и длину
    validator1 = Validator("Hello World")
    print("is_not_none:", validator1.is_not_none())  # True
    print("check_length (5, 20):", validator1.check_length(5, 20))  # True

    # Пример 2: Проверка, что строка содержит только число и оно в диапазоне
    validator2 = Validator("42")
    print("is_numeric:", validator2.is_numeric())  # True
    print("check_number_range (-100, 100):", validator2.check_number_range(-100, 100))  # True

    # Пример 3: Проверка email
    validator3 = Validator("user@example.com")
    print("is_email:", validator3.is_email())  # True

    # Пример 4: Проверка по пользовательскому regex (например, только буквы)
    validator4 = Validator("TestString")
    print("check_regex (только буквы):", validator4.check_regex(r'^[A-Za-z]+$'))  # True
