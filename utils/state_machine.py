class GestureState:
    def __init__(self):
        self.locked = False

    def can_predict(self, is_static):
        if is_static and not self.locked:
            self.locked = True
            return True

        if not is_static:
            self.locked = False

        return False
