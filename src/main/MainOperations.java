import javax.swing.*;
import java.awt.*;
import javax.swing.JRadioButton;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

/**
 * Creates the operations to be displayed.
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
public class MainOperations extends JPanel implements ActionListener
{
    private JRadioButton add, remove, fix, lock, unlock;
    private JLabel logo;
    private String operation = null;

    /**
     * The constructor created and calls the method to create the radio
     * buttons and then adds them to the pane.
     */
    public MainOperations()
    {
        super();
        setLayout(new BoxLayout(this, BoxLayout.X_AXIS));
        setBorder(BorderFactory.createEmptyBorder(4,4,4,4));
        
        buildRadioButtons();

        add.setSelected(true);
        add(add);
        add(remove);
        add(fix);
        add(lock);
        add(unlock);
    }

    /**
     * Builds all usable radio buttons.
     */
    private void buildRadioButtons()
    {
        add = new JRadioButton("Add (add)");
        add.setToolTipText("Add files to your repository.");
        add.addActionListener(this);

        remove = new JRadioButton("Remove (rm)");
        remove.setToolTipText("Remove files from your repository.");
        remove.addActionListener(this);

        fix = new JRadioButton("Fix (fix)");
        fix.setToolTipText("Try to fix things that are wrong in your repository.");
        fix.addActionListener(this);
        
        lock = new JRadioButton("Lock (lock)");
        lock.setToolTipText("Locks files in your repository");
        lock.addActionListener(this);
        
        unlock = new JRadioButton("Unlock (unlock)");
        unlock.setToolTipText("Unlocks files in your repository");
        unlock.addActionListener(this);

        return;
    }
    
    /**
     * What to do when the user checks a radio button.
     *
     * @param e The event.
     */
    public void actionPerformed(ActionEvent e) {
        Object temp = e.getSource();

        add.setSelected(false);
        remove.setSelected(false);
        fix.setSelected(false);
        lock.setSelected(false);
        unlock.setSelected(false);

        ((JRadioButton)temp).setSelected(true);

        return;
    }

    /**
     * Reads all radio buttons and returns a string containing operations 
     * that musync will accept.
     *
     * @return A string containing the option that the user wants to perform.
     */
    public String serialize()
    {
        if (add.isSelected())
            return "add";
        if (remove.isSelected())
            return "rm";
        if (fix.isSelected())
            return "fix";

        return "";
    }
}
