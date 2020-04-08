class ClampSegController:

    def __init__(self, model_class) -> None:
        """
        Initialisation of the controller. Initialises the model and a list for all views.
        """
        self.model = model_class()
        self.model.controller = self
        self.views = []

    def inform(self, data):
        """
        Informs all views currently subscribed.
        """
        for view in self.views:
            view.inform(data)

    def subscribe(self, view) -> None:
        """
        Subscribes the 'view' to the model for the inform function.
        """
        self.views.append(view)
        data = self.model.current_data()
        view.inform(data)

    def dispatch_event(self, event: str, *args) -> None:
        """
        Used by the Viewer to give commands to the model. Has different inputs and checks the strings given in 'event'.
        """
        if event == "calculate":
            frame, = args
            messages, dataset_setup,errormessage = frame.return_function()
            self.model.calculate(messages, dataset_setup,errormessage)
            frame.destroy()
        elif event == "new_project":
            self.model.new_project()
        elif event == "load_project":
            path, = args
            self.model.load_project(path)
        elif event == "save_project_as":
            path, = args
            self.model.save_project_as(path)
        elif event == "add_atf_dataset":
            atf_object, params = args
            self.model.add_atf_dataset(atf_object, **params)
        elif event == "add_abf_dataset":
            abf_object, params = args
            self.model.add_abf_dataset(abf_object, **params)
        elif event == "add_to_queue":
            ptr, = args
            self.model.add_to_queue(ptr)
        elif event == "delete_selected_dataset":
            self.model.remove_datasets()
        elif event == "remove_from_queue":
            ptr, = args
            self.model.remove_from_queue(ptr)
        elif event == "change_selection":
            sel, = args
            self.model.change_selection(sel)
        elif event == "set_metadata":
            metadata, = args
            self.model.set_metadata(metadata)
        elif event == "plot_frame_subscribe":
            frame, = args
            self.subscribe(frame)
        elif event == "export_as_csv":
            index, path = args
            self.model.export_fit_as_CSV(index, path)
        else:
            print("Error: unknown event {}".format(event))
