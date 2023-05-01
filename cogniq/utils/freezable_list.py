# Thanks, https://stackoverflow.com/questions/3942825/freeze-in-python
class FreezableList(list):
    def __init__(self, *args, **kwargs):
        self.frozen = kwargs.pop("frozen", False)
        super().__init__(*args, **kwargs)

    def __setitem__(self, i, y):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().__setitem__(i, y)

    def __delitem__(self, i):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().__delitem__(i)

    def insert(self, i, y):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().insert(i, y)

    def append(self, y):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().append(y)

    def extend(self, iterable):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().extend(iterable)

    def remove(self, y):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().remove(y)

    def pop(self, i=None):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().pop(i)

    def clear(self):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().clear()

    def sort(self, *args, **kwargs):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().sort(*args, **kwargs)

    def reverse(self):
        if self.frozen:
            raise TypeError("can't modify frozen list")
        return super().reverse()

    def freeze(self):
        self.frozen = True

    def thaw(self):
        self.frozen = False

    def copy(self):
        return FreezableList(self, frozen=self.frozen)
