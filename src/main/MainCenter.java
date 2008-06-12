import javax.swing.*;
import java.awt.*;

/**
 * Contains all instances in the center of the GUI.
 * I.e. options and files.
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
class MainCenter extends JPanel
{
    public MainOptions opts;
    public MainFiles files;

    /**
     * The constructor calls the methods to create the options pane and
     * the files pane.
     */
    public MainCenter()
    {
        super();

        setLayout(new BorderLayout());
        setBorder(BorderFactory.createEmptyBorder(4,4,4,4));

        createOptions();
        createFiles();
    }

    /**
     * Creates the options pane.
     */
    public void createOptions()
    {
        opts = new MainOptions();
        add(opts, BorderLayout.PAGE_START);

        return;
    }
    
    /**
     * Creates the file pane.
     */
    public void createFiles()
    {
        files = new MainFiles();
        add(files, BorderLayout.CENTER);

        return;
    }
}
