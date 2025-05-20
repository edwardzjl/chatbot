import styles from "./index.module.css";

import Avatar from "@mui/material/Avatar";

import { Dropdown, DropdownButton, DropdownMenu } from "@/components/DropdownMenu";
import { useUserProfile } from "@/contexts/user/hook";


const UserMenu = () => {
    const { username, avatar } = useUserProfile();

    const handleLogout = async (e) => {
        e.preventDefault();
        // See <https://oauth2-proxy.github.io/oauth2-proxy/docs/features/endpoints/>
        // This is a bit hard-coded?
        window.location.href = "/oauth2/sign_out";
    };

    return (
        <Dropdown>
            <DropdownButton className={styles.userInfoMenu}>
                <Avatar
                    // NOTE: className not working on Avatar
                    sx={{
                        width: 24,
                        height: 24,
                    }}
                    src={avatar}
                    alt={`${username}'s avatar`}
                />
            </DropdownButton>
            <DropdownMenu className={styles.userInfoMenuList}>
                <li><span>{username}</span></li>
                <hr className={styles.userInfoMenuUsernameHr} />
                <li>
                    <button
                        className={styles.userInfoMenuItem}
                        onClick={handleLogout}
                        aria-label="Logout"
                    >
                        <span className={styles.themeMenuText}>Logout</span>
                    </button>
                </li>
            </DropdownMenu>
        </Dropdown>
    );
};

export default UserMenu;
