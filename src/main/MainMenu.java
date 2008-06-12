import java.awt.*;
import javax.swing.*;
import java.awt.event.*;

/**
 * The main menu.
 *
 * Copyright: John-John Tedro, Oscar Eriksson (2008)
 *
 *   This file is part of musync-swing.
 *
 *   musync-swing is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   musync-swing is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with musync-swing.  If not, see <http://www.gnu.org/licenses/>.
 */
public class MainMenu extends JMenuBar implements ActionListener {
    private JMenu file;
    private JMenu edit;
    private JMenu help;

    private JMenuItem quit;
    private JMenuItem tmp_meta;
    private JMenuItem about;

    /**
     * The constructor only created the menu items and attach
     * action listeners to them.
     */
    public MainMenu() {
        super();

        file = new JMenu("File");
        edit = new JMenu("Edit");
        help = new JMenu("Help");

        quit = new JMenuItem("Quit");
        tmp_meta = new JMenuItem("Metadata");
        about = new JMenuItem("About");

        quit.addActionListener(this);
        tmp_meta.addActionListener(this);
        about.addActionListener(this);

        file.add(quit);
        edit.add(tmp_meta);
        help.add(about);

        add(file);
        add(edit);
        add(help);
    }

    /**
     * What to do when the different menu items are pressed.
     *
     * @param e The event.
     */
    public void actionPerformed(ActionEvent e) {
        Object src = e.getSource();

        if (src == quit) {
            System.exit(0);
            return;
        }
        
        if (src == about) {
            Commons.about.display();
            return;
        }

        if (src == tmp_meta) {
            Commons.tmp_meta.display();
        }
            
        return;
    }
}
