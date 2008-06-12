import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.io.File;
import java.util.ArrayList;
import java.util.Enumeration;
import java.lang.StringBuilder;

/**
 * The MainFiles class handles the file browsing for both files and directories.
 * Multiple files can be added at once, and also multiple directories. Everything
 * that's been added can also be removed by selecting the corresponding lines in
 * the list. The recursive option (-R) must be enabled before musync will traverse
 * directories and execute the specified operation.
 * 
 * The delete key is listened for, and if pressed down the method keyPressed will
 * be called, which will remove items untill the user releases the pressed key.
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
public class MainFiles extends JPanel implements ActionListener, KeyListener {
    private JFileChooser fc;
    private JButton addFileButton;
    private JButton addDirButton;
    private JButton removeButton;
    private JButton removeAllButton;
    private JList list;
    private ArrayList<String> items;
    private JScrollPane scrollpane;
    private GridBagConstraints c;
    private DefaultListModel dlm;

    /**
     * The constructor created the list and the buttons and add action listeners 
     * to them.
     */
    public MainFiles() {
        super();
        setLayout(new GridBagLayout());

        c = new GridBagConstraints();
        list = new JList();
        scrollpane = new JScrollPane(list);
        scrollpane.setBorder(BorderFactory.createLineBorder(new Color(0xCCCCCC)));

        addFileButton = new JButton("Add files");
        addDirButton = new JButton("Add dirs");
        removeButton = new JButton("Remove selected");
        removeAllButton = new JButton("Remove all");

        // Needed to modify the content of the list.
        dlm = new DefaultListModel();
        list.setModel(dlm);

        list.addKeyListener(this);
        addFileButton.addActionListener(this);
        addDirButton.addActionListener(this);
        removeButton.addActionListener(this);
        removeAllButton.addActionListener(this);

        // Add all children resources.
        addList();
        addFileButton();
        addDirButton();
        addRemoveButton();
        addRemoveAllButton();

        return;
    }

    /**
     * Add the list with its scrollpane.
     */
    private void addList() {
        c.fill = GridBagConstraints.BOTH;
        c.weighty = 1.0;
        c.weightx = 1.0;
        c.gridx = 0;
        c.gridy = 0;
        c.gridwidth = 5;
        c.gridheight = 2;
        add(scrollpane, c);

        return;
    }

    /**
     * Add the 'Add files' button.
     */
    private void addFileButton() {
        c.insets = new Insets(5,5,2,5);
        c.weightx = 0.0;
        c.weighty = 0.0;
        c.anchor = GridBagConstraints.PAGE_END;
        c.gridx = 0;
        c.gridy = 2;
        c.gridwidth = 1;
        c.gridheight = 1;
        add(addFileButton, c);

        return;
    }

    /**
     * Add the 'Add directories' button.
     */
    private void addDirButton() {
        c.gridx = 1;
        add(addDirButton, c);

        return;
    }

    /**
     * Add the 'Remove selected' button.
     */
    private void addRemoveButton() {
        c.gridx = 2;
        add(removeButton, c);

        return;
    }

    /**
     * Add the 'Remove all' button.
     */
    private void addRemoveAllButton() {
        c.gridx = 3;
        add(removeAllButton, c);

        return;
    }

    /**
     * What to do when a user types a key (both pressed and released).
     * This is not used, but is needed for the interface.
     *
     * @param e The key event.
     */
    public void keyTyped(KeyEvent e) {
        return;
    }

    /**
     * What to do then a key is pressed.
     *
     * @param e The key event.
     */
    public void keyPressed(KeyEvent e) {
        // Will keep deleting files as long as the user hold the 'delete' key pressed.
        if (e.getKeyCode() == KeyEvent.VK_DELETE) {
            removeSelectedLines();
        }
        else if (e.getKeyCode() == KeyEvent.VK_ESCAPE) {
            System.exit(0);
        }

        return;
    }

    /**
     * What to do then a key is released.
     * This is not used, but is needed for the interface.
     *
     * @param e The key event.
     */
    public void keyReleased(KeyEvent e) {
        return;
    }

    /**
     * What to do when the user presses a button.
     *
     * @param e The action event.
     */
    public void actionPerformed(ActionEvent e) {
        // The user wants to add files.
        if (e.getSource() == addFileButton)
            addItems(false);

        // The user wants to add directories.
        else if (e.getSource() == addDirButton)
            addItems(true);

        // The user wants to remove all selected items.
        else if (e.getSource() == removeButton)
            removeSelectedLines();

        // The user wants to remove all items added.
        else if (e.getSource() == removeAllButton)
            removeAllLines();

        return;
    }

    /**
     * Remove all the selected lines from the list.
     * After removal the next item in the list will be selected.
     * The delete key may be used to delete items.
     */
    private void removeSelectedLines() {
        int[] s = list.getSelectedIndices();
        if (s.length == 0)
            return;

        // Need the reverse the array.
        for (int a = 0, b = s.length-1; a < b; a++, b--) {
            int t = s[a]; 
            s[a] = s[b]; 
            s[b] = t;
        }

        // Remove every selected item.
        for (int i : s) {
            list.setSelectedIndex(i);
            String line = (String)list.getSelectedValue();
            items.remove(items.indexOf(line));
            dlm.remove(i);
        }
        
        // Reselect after removal.
        int size = list.getModel().getSize();
        if (s[0] >= 0 && s[0] < size)
            list.setSelectedIndex(s[0]);
        else
            list.setSelectedIndex(size-1);

        return;
    }

    /**
     * Remove all files in the list.
     */
    private void removeAllLines() {
        dlm.clear();
        items.clear();

        return;
    }

    /**
     * Add selected items.
     *
     * @param dirs True if adding directories, false if adding files.
     */
    private void addItems(boolean dirs) {
        if (fc == null)
            fc = new JFileChooser();

        fc.setMultiSelectionEnabled(true);
        if (dirs) {
            fc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
            fc.setAcceptAllFileFilterUsed(false);
        }
        else {
            fc.setFileSelectionMode(JFileChooser.FILES_ONLY);
        }

        // Add each selected item.
        if (fc.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            if (items == null)
                items = new ArrayList<String>();

            File[] sitems = fc.getSelectedFiles();
            for (File i : sitems) {
                String path = i.getAbsolutePath();
                items.add(path);
                addToList(path);
            }
        }       

        return;
    }

    /**
     * Add a selected file of directory to the JTextArea in the 'files' tab.
     *
     * @param p The path to the file or directory to be added.
     */
    private void addToList(String p) {
        dlm.addElement(p);

        JScrollBar scrollbar = scrollpane.getVerticalScrollBar();

        try {
            scrollbar.setValue(scrollbar.getMaximum()); 
        } 
        catch(Exception e) {}

        return;
    }

    /**
     * Returns all the items that the user wants to perform operations on.
     *
     * @return A space-seperated string of paths to all the added items.
     */
    public String serialize()
    {
        StringBuilder sb = new StringBuilder();
        if (items != null) {
            for(String s : items) {
                sb.append(s + " ");
            }

            sb.setLength(sb.length()-1);
        }
        return sb.toString();
    }
}
