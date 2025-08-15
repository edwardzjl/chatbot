import styles from "./index.module.css";

import { Outlet } from "react-router";

import Snackbar from "@mui/material/Snackbar";
import MuiAlert from "@mui/material/Alert";

import { useSnackbar } from "@/contexts/snackbar/hook";

import ShareConvDialog from "@/components/dialogs/ShareConvDialog";
import ConvSharedDialog from "@/components/dialogs/ConvSharedDialog";
import DeleteConvDialog from "@/components/dialogs/DeleteConvDialog";

import ChatboxHeader from "./ChatboxHeader";
import Sidebar from "./Sidebar";


const Alert = (props, ref) => {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
};


const Root = () => {
    const { snackbar, closeSnackbar } = useSnackbar();

    return (
        <div className={styles.App}>
            <Sidebar />
            <section className={styles.chatbox}>
                <ChatboxHeader />
                <Outlet />
            </section>
            <ShareConvDialog id="share-conv-dialog" />
            <ConvSharedDialog id="conv-shared-dialog" />
            <DeleteConvDialog id="del-conv-dialog" />
            <Snackbar
                open={snackbar.open}
                autoHideDuration={3000}
                onClose={closeSnackbar}
            >
                <Alert
                    severity={snackbar.severity}
                    sx={{ width: "100%" }}
                    onClose={closeSnackbar}
                >
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </div>
    );
}

export default Root;
